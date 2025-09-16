"""
Vues pour les rééducations du périnée
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction, models
from datetime import date

from core.models import Patient, ReeducationPerinee
from core.forms.reeducation_perinee import (
    ReeducationPerineeModalForm,
    ReeducationPerineeQuickForm,
    ReeducationPerineeSearchForm
)


@login_required
@require_http_methods(["GET"])
def patient_reeducations_perinee(request, patient_id):
    """
    Vue pour récupérer et afficher les séances de rééducation du périnée d'une patiente
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/reeducations_perinee/seance_history.html', {
            'seances': [],
            'patient': patient,
            'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
        })
    
    # Récupérer les séances ordonnées par numéro de séance décroissant
    seances = patient.reeducations_perinee.select_related('created_by').order_by('-numero_seance', '-date_consultation')
    
    return render(request, 'core/reeducations_perinee/seance_history.html', {
        'seances': seances,
        'patient': patient
    })


@login_required
@require_http_methods(["GET", "POST"])
def reeducation_perinee_modal(request, patient_id):
    """
    Vue pour afficher/traiter le modal de rééducation du périnée
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
        }, status=404)
    
    if request.method == 'GET':
        # Afficher le formulaire modal
        form = ReeducationPerineeModalForm(patient_id=patient.id)
        return render(request, 'core/reeducations_perinee/seance_modal.html', {
            'form': form,
            'patient': patient
        })
    
    elif request.method == 'POST':
        # Traiter la soumission du formulaire
        form = ReeducationPerineeModalForm(request.POST, patient_id=patient.id)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    seance = form.save(commit=False)
                    seance.patient = patient
                    # Associer la sage-femme connectée
                    from core.models import SageFemme
                    try:
                        # Essayer d'abord l'attribut direct
                        if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                            seance.created_by = request.user.sagefemme
                        else:
                            # Fallback: chercher la sage-femme par l'utilisateur
                            sage_femme = SageFemme.objects.filter(user=request.user).first()
                            if sage_femme:
                                seance.created_by = sage_femme
                    except Exception:
                        # Dernier recours: chercher par email si c'est un super utilisateur
                        try:
                            sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                            if sage_femme:
                                seance.created_by = sage_femme
                        except:
                            pass
                    seance.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Séance de rééducation du périnée enregistrée avec succès',
                        'seance_id': seance.id
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
def save_reeducation_perinee(request):
    """
    API pour sauvegarder une séance de rééducation du périnée via AJAX
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
                'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
            })
        
        # Traiter les données du formulaire
        with transaction.atomic():
            seance = ReeducationPerinee(patient=patient)
            
            # Associer la sage-femme connectée
            from core.models import SageFemme
            try:
                # Essayer d'abord l'attribut direct
                if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                    seance.created_by = request.user.sagefemme
                else:
                    # Fallback: chercher la sage-femme par l'utilisateur
                    sage_femme = SageFemme.objects.filter(user=request.user).first()
                    if sage_femme:
                        seance.created_by = sage_femme
            except Exception:
                # Dernier recours: chercher par email si c'est un super utilisateur
                try:
                    sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                    if sage_femme:
                        seance.created_by = sage_femme
                except:
                    pass
            
            # Date de consultation (par défaut aujourd'hui)
            date_consultation_str = request.POST.get('date_consultation')
            if date_consultation_str:
                try:
                    seance.date_consultation = date.fromisoformat(date_consultation_str)
                except ValueError:
                    seance.date_consultation = date.today()
            else:
                seance.date_consultation = date.today()
            
            # Numéro de séance
            numero_seance_str = request.POST.get('numero_seance', '1')
            try:
                seance.numero_seance = int(numero_seance_str)
                if seance.numero_seance < 1:
                    seance.numero_seance = 1
            except ValueError:
                # Calculer automatiquement le prochain numéro
                last_seance = patient.reeducations_perinee.order_by('-numero_seance').first()
                seance.numero_seance = (last_seance.numero_seance + 1) if last_seance else 1
            
            # Champs spécifiques
            seance.examen_clinique_travail = request.POST.get('examen_clinique_travail', '')
            seance.a_prevoir = request.POST.get('a_prevoir', '')
            
            # Validation et sauvegarde
            seance.full_clean()
            seance.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Séance de rééducation du périnée enregistrée avec succès',
            'seance': {
                'id': seance.id,
                'date_consultation': seance.date_consultation.isoformat(),
                'numero_seance': seance.numero_seance,
                'examen_clinique_travail': seance.examen_clinique_travail,
                'a_prevoir': seance.a_prevoir,
                'seance_resume': seance.seance_resume
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
def delete_reeducation_perinee(request, seance_id):
    """
    Vue pour supprimer une séance de rééducation du périnée
    """
    seance = get_object_or_404(ReeducationPerinee, pk=seance_id)
    patient = seance.patient
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return JsonResponse({
            'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
        }, status=404)
    
    # Supprimer la séance
    seance.delete()
    
    # Retourner l'historique mis à jour
    seances = patient.reeducations_perinee.select_related('created_by').order_by('-numero_seance', '-date_consultation')
    return render(request, 'core/reeducations_perinee/seance_history.html', {
        'seances': seances,
        'patient': patient
    })


@login_required
@require_http_methods(["GET"])
def reeducation_perinee_detail(request, seance_id):
    """
    Vue pour afficher les détails d'une séance dans un modal
    """
    seance = get_object_or_404(ReeducationPerinee, pk=seance_id)
    
    return render(request, 'core/reeducations_perinee/seance_detail_modal.html', {
        'seance': seance
    })


@login_required
@require_http_methods(["GET"])
def reeducation_perinee_quick_form(request, patient_id):
    """
    Vue pour le formulaire inline rapide de rééducation du périnée
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/reeducations_perinee/seance_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
        })
    
    form = ReeducationPerineeQuickForm(patient=patient)
    
    return render(request, 'core/reeducations_perinee/seance_inline_form.html', {
        'form': form,
        'patient': patient
    })


@login_required
@require_http_methods(["POST"])
def save_quick_reeducation_perinee(request, patient_id):
    """
    Sauvegarder une séance de rééducation du périnée rapide depuis le dropdown
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # Vérifier que c'est bien une femme
    if patient.type_patient != 'femme':
        return render(request, 'core/reeducations_perinee/seance_inline_form.html', {
            'form': None,
            'patient': patient,
            'error': 'Les séances de rééducation du périnée sont réservées aux femmes.'
        })
    
    form = ReeducationPerineeQuickForm(request.POST, patient=patient)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                seance = form.save(commit=False)
                # Associer la sage-femme connectée
                from core.models import SageFemme
                try:
                    # Essayer d'abord l'attribut direct
                    if hasattr(request.user, 'sagefemme') and request.user.sagefemme:
                        seance.created_by = request.user.sagefemme
                    else:
                        # Fallback: chercher la sage-femme par l'utilisateur
                        sage_femme = SageFemme.objects.filter(user=request.user).first()
                        if sage_femme:
                            seance.created_by = sage_femme
                except Exception:
                    # Dernier recours: chercher par email si c'est un super utilisateur
                    try:
                        sage_femme = SageFemme.objects.filter(email=request.user.email).first()
                        if sage_femme:
                            seance.created_by = sage_femme
                    except:
                        pass
                seance.save()
                
                # Retourner directement l'historique mis à jour
                seances = patient.reeducations_perinee.select_related('created_by').order_by('-numero_seance', '-date_consultation')
                response = render(request, 'core/reeducations_perinee/seance_history.html', {
                    'seances': seances,
                    'patient': patient
                })
                response['HX-Trigger'] = 'seance-form-close'
                return response
        
        except Exception as e:
            return render(request, 'core/reeducations_perinee/seance_inline_form.html', {
                'form': form,
                'patient': patient,
                'error': f'Erreur lors de la sauvegarde: {str(e)}'
            })
    
    else:
        # Retourner le formulaire avec les erreurs
        return render(request, 'core/reeducations_perinee/seance_inline_form.html', {
            'form': form,
            'patient': patient
        })


@login_required
@require_http_methods(["GET"])
def liste_reeducations_perinee(request):
    """
    Vue pour lister toutes les séances de rééducation du périnée avec recherche
    """
    form = ReeducationPerineeSearchForm(request.GET)
    
    # Base queryset
    seances = ReeducationPerinee.objects.select_related(
        'patient', 'patient__caisse', 'created_by'
    )
    
    # Filtres de recherche
    if form.is_valid():
        if form.cleaned_data.get('recherche'):
            recherche = form.cleaned_data['recherche']
            seances = seances.filter(
                models.Q(patient__nom__icontains=recherche) |
                models.Q(patient__prenom__icontains=recherche) |
                models.Q(examen_clinique_travail__icontains=recherche) |
                models.Q(a_prevoir__icontains=recherche)
            )
        
        if form.cleaned_data.get('date_debut'):
            seances = seances.filter(date_consultation__gte=form.cleaned_data['date_debut'])
        
        if form.cleaned_data.get('date_fin'):
            seances = seances.filter(date_consultation__lte=form.cleaned_data['date_fin'])
            
        if form.cleaned_data.get('numero_seance'):
            seances = seances.filter(numero_seance=form.cleaned_data['numero_seance'])
    
    # Trier par numéro de séance et date décroissants
    seances = seances.order_by('-numero_seance', '-date_consultation')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(seances, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/reeducations_perinee/liste_seances.html', {
        'form': form,
        'seances': page_obj,
        'total_seances': seances.count()
    })