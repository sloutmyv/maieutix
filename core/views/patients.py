"""
Views pour la gestion des patients
Logique métier pour le suivi des patientes
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django import forms
from django.forms import ModelForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from datetime import date
from core.models import Patient, Caisse


class PatientForm(ModelForm):
    """Formulaire pour les patients"""
    
    class Meta:
        model = Patient
        fields = [
            'type_patient', 'nom', 'prenom', 'date_naissance',
            'nom_jf', 'profession', 'telephone', 'numero_ep',
            'date_debut_grossesse', 'mere',
            'est_assure_titulaire', 'nom_assure', 'prenom_assure', 'date_naissance_assure',
            'rue_assure', 'code_postal_assure', 'commune_assure', 'caisse'
        ]
        widgets = {
            'type_patient': forms.Select(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'nom': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'prenom': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'date_naissance': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'nom_jf': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'profession': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'telephone': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'numero_ep': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'date_debut_grossesse': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'mere': forms.Select(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'est_assure_titulaire': forms.CheckboxInput(attrs={'class': 'mt-1'}),
            'nom_assure': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'prenom_assure': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'date_naissance_assure': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'rue_assure': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'code_postal_assure': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'commune_assure': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'caisse': forms.Select(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les choix de mère aux femmes actives uniquement
        self.fields['mere'].queryset = Patient.objects.filter(type_patient='femme', is_active=True)
        self.fields['mere'].empty_label = "Sélectionner une mère"
        self.fields['caisse'].queryset = Caisse.objects.all()
        self.fields['caisse'].empty_label = "Sélectionner une caisse"


@login_required
def patients_view(request):
    """
    Vue principale pour la liste des patients avec recherche
    """
    search_query = request.GET.get('search', '')
    
    # Filtrage des patients actifs
    patients = Patient.objects.filter(is_active=True).select_related('mere', 'caisse')
    
    if search_query:
        patients = patients.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(nom_jf__icontains=search_query) |
            Q(telephone__icontains=search_query) |
            Q(mere__nom__icontains=search_query) |
            Q(mere__prenom__icontains=search_query)
        )
    
    patients = patients.order_by('nom', 'prenom')
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/patients/partials/patient_table.html', {
            'patients': patients
        })
    
    context = {
        'page_title': 'Patients',
        'section': 'patients',
        'patients': patients,
        'search_query': search_query
    }
    return render(request, 'core/patients/index.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def patient_create(request):
    """
    Vue pour créer un nouveau patient
    """
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            try:
                patient = form.save()
                messages.success(request, f'Patient {patient.nom_complet} créé avec succès.')
                return JsonResponse({
                    'success': True,
                    'redirect': request.META.get('HTTP_REFERER', '/patients/')
                })
            except Exception as e:
                form.add_error(None, str(e))
        
        return render(request, 'core/patients/patient_form.html', {
            'form': form,
            'title': 'Nouveau patient',
            'submit_text': 'Créer'
        })
    
    form = PatientForm()
    return render(request, 'core/patients/patient_form.html', {
        'form': form,
        'title': 'Nouveau patient',
        'submit_text': 'Créer'
    })


@login_required
@require_http_methods(["GET", "POST"])
def patient_edit(request, patient_id):
    """
    Vue pour modifier un patient
    """
    patient = get_object_or_404(Patient, id=patient_id, is_active=True)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            try:
                patient = form.save()
                messages.success(request, f'Patient {patient.nom_complet} modifié avec succès.')
                return JsonResponse({
                    'success': True,
                    'redirect': request.META.get('HTTP_REFERER', '/patients/')
                })
            except Exception as e:
                form.add_error(None, str(e))
        
        return render(request, 'core/patients/patient_form.html', {
            'form': form,
            'patient': patient,
            'title': f'Modifier {patient.nom_complet}',
            'submit_text': 'Sauvegarder'
        })
    
    form = PatientForm(instance=patient)
    return render(request, 'core/patients/patient_form.html', {
        'form': form,
        'patient': patient,
        'title': f'Modifier {patient.nom_complet}',
        'submit_text': 'Sauvegarder'
    })


@login_required
def patient_detail(request, patient_id):
    """
    Vue pour afficher les détails d'un patient sur une page dédiée
    """
    patient = get_object_or_404(Patient, id=patient_id, is_active=True)
    
    context = {
        'patient': patient,
        'bebes': patient.get_bebes() if patient.type_patient == 'femme' else None,
        'page_title': f'Patient - {patient.nom_complet}',
        'section': 'patients'
    }
    
    return render(request, 'core/patients/patient_detail_page.html', context)


@login_required
def patient_detail_modal(request, patient_id):
    """
    Vue pour afficher les détails d'un patient en modal (conservée pour compatibilité)
    """
    patient = get_object_or_404(Patient, id=patient_id, is_active=True)
    
    context = {
        'patient': patient,
        'bebes': patient.get_bebes() if patient.type_patient == 'femme' else None
    }
    
    return render(request, 'core/patients/patient_detail.html', context)


@login_required
@require_http_methods(["POST"])
def patient_toggle_active(request, patient_id):
    """
    Vue pour activer/désactiver un patient
    """
    patient = get_object_or_404(Patient, id=patient_id)
    
    patient.is_active = not patient.is_active
    patient.save()
    
    status = "activé" if patient.is_active else "désactivé"
    messages.success(request, f'Patient {patient.nom_complet} {status} avec succès.')
    
    return JsonResponse({
        'success': True,
        'is_active': patient.is_active
    })


@login_required
def search_meres(request):
    """
    Vue pour l'autocomplétion de recherche des mères
    """
    query = request.GET.get('q', '').strip()
    
    # Rechercher parmi toutes les femmes actives
    meres = Patient.objects.filter(
        type_patient='femme',
        is_active=True
    )
    
    if query and len(query) >= 2:
        meres = meres.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(nom_jf__icontains=query)
        )
    
    # Limiter les résultats
    limit = 10 if query else 50  # Plus de résultats si pas de recherche (pour l'initialisation)
    meres = meres.order_by('nom', 'prenom')[:limit]
    
    results = []
    for mere in meres:
        results.append({
            'id': mere.id,
            'nom_complet': mere.nom_complet,
            'date_naissance_formatted': mere.date_naissance.strftime('%d/%m/%Y')
        })
    
    return JsonResponse(results, safe=False)


