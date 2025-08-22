"""
Middleware d'authentification pour forcer le changement de mot de passe
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout


class ForcePasswordChangeMiddleware:
    """
    Middleware qui force le changement de mot de passe pour les utilisateurs 
    qui utilisent encore le mot de passe par défaut
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs exemptées de la vérification
        exempt_urls = [
            reverse('auth:login'),
            reverse('auth:logout'),
            reverse('auth:change_password_required'),
            '/admin/',  # Interface admin
        ]
        
        # Vérifier si l'utilisateur est connecté
        if (request.user.is_authenticated and 
            hasattr(request.user, 'must_change_password') and 
            request.user.must_change_password):
            
            # Permettre l'accès aux URLs exemptées
            if any(request.path.startswith(url) for url in exempt_urls):
                response = self.get_response(request)
                return response
            
            # Rediriger vers la page de changement de mot de passe obligatoire
            return redirect('auth:change_password_required')
        
        response = self.get_response(request)
        return response