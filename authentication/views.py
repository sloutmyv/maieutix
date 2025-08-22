"""
Vues d'authentification pour les sages-femmes
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from authentication.models import SageFemmeUser
from core.models.sagefemme import SageFemme


class LoginForm(forms.Form):
    """Formulaire de connexion"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary',
            'placeholder': 'votre@email.nc'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary',
            'placeholder': 'Votre mot de passe'
        })
    )


class ChangePasswordForm(forms.Form):
    """Formulaire de changement de mot de passe"""
    current_password = forms.CharField(
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary',
            'placeholder': 'Mot de passe actuel'
        })
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary',
            'placeholder': 'Nouveau mot de passe'
        }),
        help_text="Le mot de passe doit contenir au moins 8 caractères."
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary',
            'placeholder': 'Confirmer le mot de passe'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        """Vérifier le mot de passe actuel"""
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return current_password
    
    def clean_new_password2(self):
        """Vérifier que les deux mots de passe correspondent"""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
            
            # Validation minimale du mot de passe
            if len(new_password1) < 8:
                raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
                
        return new_password2
    
    def save(self):
        """Sauvegarder le nouveau mot de passe"""
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        self.user.must_change_password = False
        self.user.save()


@csrf_protect
def login_view(request):
    """Vue de connexion"""
    # Rediriger si déjà connecté
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Vérifier si l'utilisateur doit changer son mot de passe
                    if user.must_change_password:
                        messages.warning(
                            request, 
                            "Vous devez changer votre mot de passe par défaut avant de continuer."
                        )
                        return redirect('auth:change_password_required')
                    
                    # Redirection après connexion réussie
                    next_url = request.GET.get('next', 'home')
                    messages.success(request, f"Bienvenue {user.email} !")
                    return redirect(next_url)
                else:
                    messages.error(request, "Votre compte est désactivé.")
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login.html', {
        'form': form,
        'page_title': 'Connexion'
    })


def logout_view(request):
    """Vue de déconnexion"""
    if request.user.is_authenticated:
        messages.success(request, "Vous avez été déconnecté avec succès.")
    logout(request)
    return redirect('auth:login')


@login_required
@csrf_protect
def change_password_view(request):
    """Vue de changement de mot de passe"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            
            # Réauthentifier l'utilisateur avec le nouveau mot de passe
            user = authenticate(
                request, 
                username=request.user.email, 
                password=form.cleaned_data['new_password1']
            )
            if user:
                login(request, user)
            
            return redirect('home')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'core/auth/change_password.html', {
        'form': form,
        'page_title': 'Changer le mot de passe'
    })


@login_required
@csrf_protect  
def change_password_required_view(request):
    """Vue pour forcer le changement de mot de passe (première connexion)"""
    # Si l'utilisateur n'a pas besoin de changer son mot de passe, rediriger
    if not request.user.must_change_password:
        return redirect('home')
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                "Votre mot de passe a été modifié avec succès. Vous pouvez maintenant utiliser l'application."
            )
            
            # Réauthentifier l'utilisateur
            user = authenticate(
                request, 
                username=request.user.email, 
                password=form.cleaned_data['new_password1']
            )
            if user:
                login(request, user)
            
            return redirect('home')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'core/auth/change_password_required.html', {
        'form': form,
        'page_title': 'Changement de mot de passe obligatoire',
        'is_required': True
    })