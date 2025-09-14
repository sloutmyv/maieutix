"""
Vues pour les consultations de préparation à la naissance
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction, models
from datetime import date

from core.models import Patient, ConsultationPreparationNaissance
from core.forms.consultation_preparation_naissance import (
    ConsultationPreparationNaissanceModalForm,
    ConsultationPreparationNaissanceQuickForm,
    ConsultationPreparationNaissanceSearchForm
)


@login_required
@require_http_methods(["GET"])
def patient_consultations_preparation_naissance(request, patient_id):
    """
    Vue pour récupérer et afficher les consultations de préparation à la naissance d'une patiente
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/consultations_preparation_naissance/consultation_history.html', {
            'consultations': [],
            'patient': patient,
            'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
        })
    
    # Récupérer les consultations ordonnées par date décroissante
    consultations = patient.consultations_preparation_naissance.select_related('created_by').all()
    
    return render(request, 'core/consultations_preparation_naissance/consultation_history.html', {
        'consultations': consultations,
        'patient': patient
    })


@login_required
@require_http_methods(["GET", "POST"])
def consultation_preparation_naissance_modal(request, patient_id):
    """
    Vue pour afficher/traiter le modal de consultation de préparation à la naissance
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
        }, status=404)
    
    if request.method == 'GET':
        # Afficher le formulaire modal
        form = ConsultationPreparationNaissanceModalForm(patient_id=patient.id)
        return render(request, 'core/consultations_preparation_naissance/consultation_modal.html', {
            'form': form,
            'patient': patient
        })
    
    elif request.method == 'POST':
        # Traiter la soumission du formulaire
        form = ConsultationPreparationNaissanceModalForm(request.POST, patient_id=patient.id)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    consultation = form.save(commit=False)
                    consultation.patient = patient
                    # Associer la sage-femme connectée
                    from core.models import SageFemme
                    try:
                        # Essayer d'abord l'attribut direct
                        if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                            consultation.created_by = request.user.sagefemme
                        else:
                            # Fallback: chercher la sage-femme par l'utilisateur
                            sage_femme = SageFemme.objects.filter(user=request.user).first()
                            if sage_femme:
                                consultation.created_by = sage_femme
                    except Exception:
                        # Dernier recours: chercher par email si c'est un super utilisateur
                        try:
                            sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                            if sage_femme:
                                consultation.created_by = sage_femme
                        except:
                            pass
                    consultation.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Consultation de préparation à la naissance enregistrée avec succès',
                        'consultation_id': consultation.id
                    })
            except Exception as e:
                form.add_error(None, f'Erreur lors de la sauvegarde: {str(e)}')
        
        # Retourner une réponse JSON avec les erreurs
        return JsonResponse({
            'success': False,
            'error': 'Formulaire invalide',
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def save_consultation_preparation_naissance(request):
    """
    API pour sauvegarder une consultation de préparation à la naissance via AJAX
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
        
        # Vérifier que c'est bien une femme
        if patient.type_patient != 'femme':
            return JsonResponse({
                'success': False,
                'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
            })
        
        # Traiter les données du formulaire
        with transaction.atomic():
            consultation = ConsultationPreparationNaissance(patient=patient)
            
            # Associer la sage-femme connectée
            from core.models import SageFemme
            try:
                # Essayer d'abord l'attribut direct
                if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                    consultation.created_by = request.user.sagefemme
                else:
                    # Fallback: chercher la sage-femme par l'utilisateur
                    sage_femme = SageFemme.objects.filter(user=request.user).first()
                    if sage_femme:
                        consultation.created_by = sage_femme
            except Exception:
                # Dernier recours: chercher par email si c'est un super utilisateur
                try:
                    sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                    if sage_femme:
                        consultation.created_by = sage_femme
                except:
                    pass
            
            # Date de consultation (par défaut aujourd'hui)
            date_consultation_str = request.POST.get('date_consultation')
            if date_consultation_str:
                try:
                    consultation.date_consultation = date.fromisoformat(date_consultation_str)
                except ValueError:
                    consultation.date_consultation = date.today()
            else:
                consultation.date_consultation = date.today()
            
            # Champs spécifiques
            consultation.theme_aborde = request.POST.get('theme_aborde', '')
            consultation.a_prevoir = request.POST.get('a_prevoir', '')
            
            # Validation et sauvegarde
            consultation.full_clean()
            consultation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Consultation de préparation à la naissance enregistrée avec succès',
            'consultation': {
                'id': consultation.id,
                'date_consultation': consultation.date_consultation.isoformat(),
                'semaines_amenorrhee': consultation.semaines_amenorrhee,
                'theme_aborde': consultation.theme_aborde,
                'a_prevoir': consultation.a_prevoir,
                'consultation_resume': consultation.consultation_resume
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
def delete_consultation_preparation_naissance(request, consultation_id):
    """
    Vue pour supprimer une consultation de préparation à la naissance
    """
    consultation = get_object_or_404(ConsultationPreparationNaissance, pk=consultation_id)
    patient = consultation.patient
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
        }, status=404)
    
    # Supprimer la consultation
    consultation.delete()
    
    # Retourner l'historique mis à jour
    consultations = patient.consultations_preparation_naissance.select_related('created_by').all()
    return render(request, 'core/consultations_preparation_naissance/consultation_history.html', {
        'consultations': consultations,
        'patient': patient
    })


@login_required
@require_http_methods(["GET"])
def consultation_preparation_naissance_detail(request, consultation_id):
    """
    Vue pour afficher les détails d'une consultation dans un modal
    """
    consultation = get_object_or_404(ConsultationPreparationNaissance, pk=consultation_id)
    
    return render(request, 'core/consultations_preparation_naissance/consultation_detail_modal.html', {
        'consultation': consultation
    })


@login_required
@require_http_methods(["GET"])
def consultation_preparation_naissance_quick_form(request, patient_id):
    """
    Vue pour le formulaire inline rapide de consultation de préparation à la naissance
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/consultations_preparation_naissance/consultation_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
        })
    
    form = ConsultationPreparationNaissanceQuickForm(patient=patient)
    
    return render(request, 'core/consultations_preparation_naissance/consultation_inline_form.html', {
        'form': form,
        'patient': patient
    })


@login_required
@require_http_methods(["POST"])
def save_quick_consultation_preparation_naissance(request, patient_id):
    """
    Sauvegarder une consultation de préparation à la naissance rapide depuis le dropdown
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/consultations_preparation_naissance/consultation_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
        })
    
    form = ConsultationPreparationNaissanceQuickForm(request.POST, patient=patient)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                consultation = form.save(commit=False)
                # Associer la sage-femme connectée
                from core.models import SageFemme
                try:
                    # Essayer d'abord l'attribut direct
                    if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                        consultation.created_by = request.user.sagefemme
                    else:
                        # Fallback: chercher la sage-femme par l'utilisateur
                        sage_femme = SageFemme.objects.filter(user=request.user).first()
                        if sage_femme:
                            consultation.created_by = sage_femme
                except Exception:
                    # Dernier recours: chercher par email si c'est un super utilisateur
                    try:
                        sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                        if sage_femme:
                            consultation.created_by = sage_femme
                    except:
                        pass
                consultation.save()
                
                # Retourner directement l'historique mis à jour
                consultations = patient.consultations_preparation_naissance.select_related('created_by').all()
                response = render(request, 'core/consultations_preparation_naissance/consultation_history.html', {
                    'consultations': consultations,
                    'patient': patient
                })
                response['HX-Trigger'] = 'consultation-form-close'
                return response
        
        except Exception as e:
            return render(request, 'core/consultations_preparation_naissance/consultation_inline_form.html', {
                'form': form,
                'patient': patient,
                'error': f'Erreur lors de la sauvegarde: {str(e)}'
            })
    
    else:
        # Retourner le formulaire avec les erreurs
        return render(request, 'core/consultations_preparation_naissance/consultation_inline_form.html', {
            'form': form,
            'patient': patient
        })


@login_required
@require_http_methods(["GET"])
def liste_consultations_preparation_naissance(request):
    """
    Vue pour lister toutes les consultations de préparation à la naissance avec recherche
    """
    form = ConsultationPreparationNaissanceSearchForm(request.GET)
    
    # Base queryset
    consultations = ConsultationPreparationNaissance.objects.select_related(
        'patient', 'patient__caisse', 'created_by'
    )
    
    # Filtres de recherche
    if form.is_valid():
        if form.cleaned_data.get('recherche'):
            recherche = form.cleaned_data['recherche']
            consultations = consultations.filter(
                models.Q(patient__nom__icontains=recherche) |
                models.Q(patient__prenom__icontains=recherche) |
                models.Q(theme_aborde__icontains=recherche) |
                models.Q(a_prevoir__icontains=recherche)
            )
        
        if form.cleaned_data.get('date_debut'):
            consultations = consultations.filter(date_consultation__gte=form.cleaned_data['date_debut'])
        
        if form.cleaned_data.get('date_fin'):
            consultations = consultations.filter(date_consultation__lte=form.cleaned_data['date_fin'])
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(consultations, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/consultations_preparation_naissance/liste_consultations.html', {
        'form': form,
        'consultations': page_obj,
        'total_consultations': consultations.count()
    })