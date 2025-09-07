"""
Vues pour les consultations obstétricales
"""

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import date

from core.models import Patient, ConsultationObstetricale
from core.forms.consultation_obstetricale import (
    ConsultationObstetricaleModalForm,
    ConsultationObstetricaleQuickForm
)


@login_required
@require_http_methods(["GET"])
def patient_consultations_obstetricales(request, patient_id):
    """
    Vue pour récupérer et afficher les consultations d'une patiente
    """
    try:
        patient = get_object_or_404(Patient, pk=patient_id)
        
        # Vérifier que c'est bien une femme
        if patient.type_patient != 'femme':
            return render(request, 'core/consultations_obstetricales/consultation_history.html', {
                'consultations': [],
                'patient': patient,
                'error': 'Les consultations obstétricales sont réservées aux femmes.'
            })
        
        # Récupérer les consultations ordonnées par date décroissante
        consultations = patient.consultations_obstetricales.select_related('created_by').all()
        
        return render(request, 'core/consultations_obstetricales/consultation_history.html', {
            'consultations': consultations,
            'patient': patient
        })
        
    except Exception as e:
        return render(request, 'core/consultations_obstetricales/consultation_history.html', {
            'consultations': [],
            'patient': None,
            'error': f'Erreur lors de la récupération des consultations: {str(e)}'
        })


@login_required
@require_http_methods(["GET", "POST"])
def consultation_obstetricale_modal(request, patient_id):
    """
    Vue pour afficher/traiter le modal de consultation
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les consultations obstétricales sont réservées aux femmes.'
        }, status=404)
    
    if request.method == 'GET':
        # Afficher le formulaire modal
        form = ConsultationObstetricaleModalForm(patient_id=patient.id)
        return render(request, 'core/consultations_obstetricales/consultation_modal.html', {
            'form': form,
            'patient': patient
        })
    
    elif request.method == 'POST':
        # Traiter la soumission du formulaire
        form = ConsultationObstetricaleModalForm(request.POST, patient_id=patient.id)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    consultation = form.save(commit=False)
                    consultation.patient = patient
                    # Associer la sage-femme connectée
                    if hasattr(request.user, 'sagefemme'):
                        consultation.created_by = request.user.sagefemme
                    consultation.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Consultation enregistrée avec succès',
                    'consultation_id': consultation.id,
                    'date_consultation': consultation.date_consultation.isoformat()
                })
            
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Erreur lors de la sauvegarde: {str(e)}'
                })
        else:
            # Retourner le formulaire avec les erreurs
            return render(request, 'core/consultations_obstetricales/consultation_modal.html', {
                'form': form,
                'patient': patient
            })


@login_required
@require_http_methods(["POST"])
def save_consultation_obstetricale(request):
    """
    API pour sauvegarder une consultation via AJAX
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
                'error': 'Les consultations obstétricales sont réservées aux femmes.'
            })
        
        # Traiter les données du formulaire
        with transaction.atomic():
            consultation = ConsultationObstetricale(patient=patient)
            
            # Associer la sage-femme connectée
            if hasattr(request.user, 'sagefemme'):
                consultation.created_by = request.user.sagefemme
            
            # Date de consultation (par défaut aujourd'hui)
            date_consultation_str = request.POST.get('date_consultation')
            if date_consultation_str:
                try:
                    consultation.date_consultation = date.fromisoformat(date_consultation_str)
                except ValueError:
                    consultation.date_consultation = date.today()
            else:
                consultation.date_consultation = date.today()
            
            # Constantes vitales
            tension_sys = request.POST.get('tension_systolique')
            if tension_sys:
                try:
                    consultation.tension_systolique = int(tension_sys)
                except ValueError:
                    pass
            
            tension_dia = request.POST.get('tension_diastolique')
            if tension_dia:
                try:
                    consultation.tension_diastolique = int(tension_dia)
                except ValueError:
                    pass
            
            poids = request.POST.get('poids')
            if poids:
                try:
                    consultation.poids = float(poids)
                except ValueError:
                    pass
            
            # Champs texte
            consultation.motif = request.POST.get('motif', '')
            consultation.examen = request.POST.get('examen', '')
            consultation.prescription = request.POST.get('prescription', '')
            consultation.notes = request.POST.get('notes', '')
            
            # Validation et sauvegarde
            consultation.full_clean()
            consultation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Consultation enregistrée avec succès',
            'consultation': {
                'id': consultation.id,
                'date_consultation': consultation.date_consultation.isoformat(),
                'motif': consultation.motif,
                'tension_complete': consultation.tension_complete,
                'tension_interpretation': consultation.tension_interpretation,
                'poids': consultation.poids,
                'imc': consultation.imc
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
def delete_consultation_obstetricale(request, consultation_id):
    """
    Vue pour supprimer une consultation
    """
    try:
        consultation = get_object_or_404(ConsultationObstetricale, pk=consultation_id)
        patient = consultation.patient
        
        # Vérifier que c'est bien une femme
        if patient.type_patient != 'femme':
            return JsonResponse({
                'error': 'Les consultations obstétricales sont réservées aux femmes.'
            }, status=404)
        
        # Supprimer la consultation
        consultation.delete()
        
        # Retourner l'historique mis à jour
        consultations = patient.consultations_obstetricales.select_related('created_by').all()
        return render(request, 'core/consultations_obstetricales/consultation_history.html', {
            'consultations': consultations,
            'patient': patient
        })
        
    except Exception as e:
        return render(request, 'core/consultations_obstetricales/consultation_history.html', {
            'consultations': [],
            'patient': None,
            'error': f'Erreur lors de la suppression: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def consultation_obstetricale_detail(request, consultation_id):
    """
    Vue pour afficher les détails d'une consultation dans un modal
    """
    try:
        consultation = get_object_or_404(ConsultationObstetricale, pk=consultation_id)
        
        return render(request, 'core/consultations_obstetricales/consultation_detail_modal.html', {
            'consultation': consultation
        })
        
    except Exception as e:
        return render(request, 'core/consultations_obstetricales/consultation_history.html', {
            'consultations': [],
            'patient': None,
            'error': f'Erreur lors de la récupération: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def consultation_obstetricale_quick_form(request, patient_id):
    """
    Vue pour le formulaire inline complet de consultation
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/consultations_obstetricales/consultation_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les consultations obstétricales sont réservées aux femmes.'
        })
    
    form = ConsultationObstetricaleQuickForm(patient=patient)
    
    return render(request, 'core/consultations_obstetricales/consultation_inline_form.html', {
        'form': form,
        'patient': patient
    })


@login_required
@require_http_methods(["POST"])
def save_quick_consultation_obstetricale(request, patient_id):
    """
    Sauvegarder une consultation rapide depuis le dropdown
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les consultations obstétricales sont réservées aux femmes.'
        }, status=404)
    
    form = ConsultationObstetricaleQuickForm(request.POST, patient=patient)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                consultation = form.save(commit=False)
                # Associer la sage-femme connectée
                if hasattr(request.user, 'sagefemme'):
                    consultation.created_by = request.user.sagefemme
                consultation.save()
                
                # Retourner directement l'historique mis à jour
                consultations = patient.consultations_obstetricales.select_related('created_by').all()
                response = render(request, 'core/consultations_obstetricales/consultation_history.html', {
                    'consultations': consultations,
                    'patient': patient
                })
                response['HX-Trigger'] = 'consultation-form-close'
                return response
        
        except Exception as e:
            return render(request, 'core/consultations_obstetricales/consultation_inline_form.html', {
                'form': form,
                'patient': patient,
                'error': f'Erreur lors de la sauvegarde: {str(e)}'
            })
    
    else:
        # Retourner le formulaire avec les erreurs
        return render(request, 'core/consultations_obstetricales/consultation_inline_form.html', {
            'form': form,
            'patient': patient
        })