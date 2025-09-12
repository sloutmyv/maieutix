"""
Vues pour les entretiens prénataux précoces
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction, models
from datetime import date

from core.models import Patient, EntretienPrenatalPrecoce
from core.forms.entretien_prenatal_precoce import (
    EntretienPrenatalPrecoceModalForm,
    EntretienPrenatalPrecoceQuickForm,
    EntretienPrenatalPrecoceSearchForm
)


@login_required
@require_http_methods(["GET"])
def patient_entretiens_prenataux_precoces(request, patient_id):
    """
    Vue pour récupérer et afficher les entretiens prénataux précoces d'une patiente
    """
    try:
        patient = get_object_or_404(Patient, pk=patient_id)
        
        # Vérifier que c'est bien une femme
        if patient.type_patient != 'femme':
            return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
                'entretiens': [],
                'patient': patient,
                'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
            })
        
        # Vérifier qu'elle a une DDG définie
        if not patient.date_debut_grossesse:
            return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
                'entretiens': [],
                'patient': patient,
                'error': 'La patiente doit avoir une date de début de grossesse définie.'
            })
        
        # Récupérer les entretiens ordonnés par date décroissante
        entretiens = patient.entretiens_prenataux_precoces.select_related('sage_femme', 'created_by').all()
        
        return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
            'entretiens': entretiens,
            'patient': patient
        })
        
    except Exception as e:
        return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
            'entretiens': [],
            'patient': None,
            'error': f'Erreur lors de la récupération des entretiens: {str(e)}'
        })


@login_required
@require_http_methods(["GET", "POST"])
def entretien_prenatal_precoce_modal(request, patient_id):
    """
    Vue pour afficher/traiter le modal d'entretien prénatal précoce
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme avec DDG
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
        }, status=404)
    
    if not patient.date_debut_grossesse:
        return JsonResponse({
            'error': 'La patiente doit avoir une date de début de grossesse définie.'
        }, status=404)
    
    if request.method == 'GET':
        # Afficher le formulaire modal
        form = EntretienPrenatalPrecoceModalForm(patient_id=patient.id)
        return render(request, 'core/entretiens_prenataux_precoces/entretien_detail_modal.html', {
            'form': form,
            'patient': patient
        })
    
    elif request.method == 'POST':
        # Traiter la soumission du formulaire
        form = EntretienPrenatalPrecoceModalForm(request.POST, patient_id=patient.id)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    entretien = form.save(commit=False)
                    entretien.patient = patient
                    # Associer la sage-femme connectée
                    if hasattr(request.user, 'sagefemme'):
                        entretien.sage_femme = request.user.sagefemme
                        entretien.created_by = request.user.sagefemme
                    entretien.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Entretien prénatal précoce enregistré avec succès',
                    'entretien_id': entretien.id,
                    'date_entretien': entretien.date_entretien.isoformat()
                })
            
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Erreur lors de la sauvegarde: {str(e)}'
                })
        else:
            # Retourner le formulaire avec les erreurs
            return render(request, 'core/entretiens_prenataux_precoces/entretien_detail_modal.html', {
                'form': form,
                'patient': patient
            })


@login_required
@require_http_methods(["POST"])
def save_entretien_prenatal_precoce(request):
    """
    API pour sauvegarder un entretien prénatal précoce via AJAX
    """
    try:
        # Récupérer l'ID de la patiente
        patient_id = request.POST.get('patient_id')
        if not patient_id:
            return JsonResponse({
                'success': False,
                'error': 'Patient ID manquant'
            })
        
        patient = get_object_or_404(Patient, pk=patient_id)
        
        # Vérifier que c'est bien une femme avec DDG
        if patient.type_patient != 'femme':
            return JsonResponse({
                'success': False,
                'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
            })
        
        if not patient.date_debut_grossesse:
            return JsonResponse({
                'success': False,
                'error': 'La patiente doit avoir une date de début de grossesse définie.'
            })
        
        # Traiter les données du formulaire
        with transaction.atomic():
            entretien = EntretienPrenatalPrecoce(patient=patient)
            
            # Associer la sage-femme connectée
            if hasattr(request.user, 'sagefemme'):
                entretien.sage_femme = request.user.sagefemme
                entretien.created_by = request.user.sagefemme
            
            # Date d'entretien (par défaut aujourd'hui)
            date_entretien_str = request.POST.get('date_entretien')
            if date_entretien_str:
                try:
                    entretien.date_entretien = date.fromisoformat(date_entretien_str)
                except ValueError:
                    entretien.date_entretien = date.today()
            else:
                entretien.date_entretien = date.today()
            
            # Présence conjoint
            entretien.conjoint_present = request.POST.get('conjoint_present') == 'on'
            
            # Champs texte
            entretien.lieu_accouchement_prevu = request.POST.get('lieu_accouchement_prevu', '')
            entretien.atcd_marquants = request.POST.get('atcd_marquants', '')
            entretien.environnement_social_familial = request.POST.get('environnement_social_familial', '')
            entretien.projet_naissance = request.POST.get('projet_naissance', '')
            entretien.projet_parental = request.POST.get('projet_parental', '')
            entretien.ressenti = request.POST.get('ressenti', '')
            entretien.propositions_liens = request.POST.get('propositions_liens', '')
            entretien.notes = request.POST.get('notes', '')
            
            # Validation et sauvegarde
            entretien.full_clean()
            entretien.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Entretien prénatal précoce enregistré avec succès',
            'entretien': {
                'id': entretien.id,
                'date_entretien': entretien.date_entretien.isoformat(),
                'semaines_amenorrhee': entretien.semaines_amenorrhee,
                'conjoint_present': entretien.conjoint_present,
                'lieu_accouchement_prevu': entretien.lieu_accouchement_prevu,
                'entretien_resume': entretien.entretien_resume
            }
        })
    
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur de validation: {str(e)}'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la sauvegarde: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def delete_entretien_prenatal_precoce(request, entretien_id):
    """
    Vue pour supprimer un entretien prénatal précoce
    """
    try:
        entretien = get_object_or_404(EntretienPrenatalPrecoce, pk=entretien_id)
        patient = entretien.patient
        
        # Vérifier que c'est bien une femme
        if patient.type_patient != 'femme':
            return JsonResponse({
                'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
            }, status=404)
        
        # Supprimer l'entretien
        entretien.delete()
        
        # Retourner l'historique mis à jour
        entretiens = patient.entretiens_prenataux_precoces.select_related('sage_femme', 'created_by').all()
        return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
            'entretiens': entretiens,
            'patient': patient
        })
        
    except Exception as e:
        return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
            'entretiens': [],
            'patient': None,
            'error': f'Erreur lors de la suppression: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def entretien_prenatal_precoce_detail(request, entretien_id):
    """
    Vue pour afficher les détails d'un entretien dans un modal
    """
    try:
        entretien = get_object_or_404(EntretienPrenatalPrecoce, pk=entretien_id)
        
        return render(request, 'core/entretiens_prenataux_precoces/entretien_detail_modal.html', {
            'entretien': entretien
        })
        
    except Exception as e:
        return render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
            'entretiens': [],
            'patient': None,
            'error': f'Erreur lors de la récupération: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def entretien_prenatal_precoce_quick_form(request, patient_id):
    """
    Vue pour le formulaire inline rapide d'entretien prénatal précoce
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme avec DDG
    if patient.type_patient != 'femme':
        return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
        })
    
    if not patient.date_debut_grossesse:
        return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'La patiente doit avoir une date de début de grossesse définie.'
        })
    
    form = EntretienPrenatalPrecoceQuickForm(patient=patient)
    
    return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
        'form': form,
        'patient': patient
    })


@login_required
@require_http_methods(["POST"])
def save_quick_entretien_prenatal_precoce(request, patient_id):
    """
    Sauvegarder un entretien prénatal précoce rapide depuis le dropdown
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme avec DDG
    if patient.type_patient != 'femme':
        return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les entretiens prénataux précoces sont réservés aux femmes.'
        })
    
    if not patient.date_debut_grossesse:
        return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'La patiente doit avoir une date de début de grossesse définie.'
        })
    
    form = EntretienPrenatalPrecoceQuickForm(request.POST, patient=patient)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                entretien = form.save(commit=False)
                # Associer la sage-femme connectée
                if hasattr(request.user, 'sagefemme'):
                    entretien.sage_femme = request.user.sagefemme
                    entretien.created_by = request.user.sagefemme
                entretien.save()
                
                # Retourner directement l'historique mis à jour
                entretiens = patient.entretiens_prenataux_precoces.select_related('sage_femme', 'created_by').all()
                response = render(request, 'core/entretiens_prenataux_precoces/entretien_history.html', {
                    'entretiens': entretiens,
                    'patient': patient
                })
                response['HX-Trigger'] = 'entretien-form-close'
                return response
        
        except Exception as e:
            return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
                'form': form,
                'patient': patient,
                'error': f'Erreur lors de la sauvegarde: {str(e)}'
            })
    
    else:
        # Retourner le formulaire avec les erreurs
        return render(request, 'core/entretiens_prenataux_precoces/entretien_inline_form.html', {
            'form': form,
            'patient': patient
        })


@login_required
@require_http_methods(["GET"])
def liste_entretiens_prenataux_precoces(request):
    """
    Vue pour lister tous les entretiens prénataux précoces avec recherche
    """
    form = EntretienPrenatalPrecoceSearchForm(request.GET)
    
    # Base queryset
    entretiens = EntretienPrenatalPrecoce.objects.select_related(
        'patient', 'patient__caisse', 'sage_femme', 'created_by'
    )
    
    # Filtres de recherche
    if form.is_valid():
        if form.cleaned_data.get('recherche'):
            recherche = form.cleaned_data['recherche']
            entretiens = entretiens.filter(
                models.Q(patient__nom__icontains=recherche) |
                models.Q(patient__prenom__icontains=recherche) |
                models.Q(lieu_accouchement_prevu__icontains=recherche) |
                models.Q(atcd_marquants__icontains=recherche) |
                models.Q(projet_naissance__icontains=recherche)
            )
        
        if form.cleaned_data.get('date_debut'):
            entretiens = entretiens.filter(date_entretien__gte=form.cleaned_data['date_debut'])
        
        if form.cleaned_data.get('date_fin'):
            entretiens = entretiens.filter(date_entretien__lte=form.cleaned_data['date_fin'])
        
        if form.cleaned_data.get('conjoint_present'):
            conjoint_present = form.cleaned_data['conjoint_present'] == 'oui'
            entretiens = entretiens.filter(conjoint_present=conjoint_present)
        
        if form.cleaned_data.get('sage_femme'):
            entretiens = entretiens.filter(sage_femme=form.cleaned_data['sage_femme'])
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(entretiens, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/entretiens_prenataux_precoces/liste_entretiens.html', {
        'form': form,
        'entretiens': page_obj,
        'total_entretiens': entretiens.count()
    })