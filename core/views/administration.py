"""
Views pour l'administration
Logique métier pour la gestion administrative
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q
from django import forms
from django.forms import ModelForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from datetime import date, datetime
from core.models.sagefemme import SageFemme
from core.models.periode_activite import PeriodeActivite


class SageFemmeForm(ModelForm):
    """Formulaire pour les sages-femmes"""
    
    class Meta:
        model = SageFemme
        fields = [
            'nom', 'prenom', 'titre', 'telephone', 'email',
            'rue', 'code_postal', 'ville',
            'numero_cafat', 'ridet', 'rib', 'banque',
            'situation', 'remplacement_de',
            'etat_recapitulatif_commun', 'bons_depot_communs',
            'is_active'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'prenom': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'titre': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'telephone': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'rue': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'code_postal': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'ville': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'numero_cafat': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'ridet': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'rib': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'banque': forms.TextInput(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'remplacement_de': forms.Select(attrs={'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'}),
            'etat_recapitulatif_commun': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-primary focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50'}),
            'bons_depot_communs': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-primary focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-primary focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrer les choix pour remplacement_de
        if 'remplacement_de' in self.fields:
            self.fields['remplacement_de'].queryset = SageFemme.objects.filter(
                situation__in=['titulaire', 'collaborateur']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
    
    def clean_email(self):
        """Valide l'unicité de l'email"""
        email = self.cleaned_data.get('email')
        if email:
            queryset = SageFemme.objects.filter(email=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Une sage-femme avec cet email existe déjà.")
        return email
    
    def clean_numero_cafat(self):
        """Valide l'unicité du numéro CAFAT"""
        numero_cafat = self.cleaned_data.get('numero_cafat')
        if numero_cafat:
            queryset = SageFemme.objects.filter(numero_cafat=numero_cafat)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Une sage-femme avec ce numéro CAFAT existe déjà.")
        return numero_cafat
    
    def clean_ridet(self):
        """Valide l'unicité du RIDET"""
        ridet = self.cleaned_data.get('ridet')
        if ridet:
            queryset = SageFemme.objects.filter(ridet=ridet)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Une sage-femme avec ce RIDET existe déjà.")
        return ridet


def check_titulaire_permission(request):
    """Vérifie si l'utilisateur a les permissions d'administration (titulaire)"""
    # Super admin a toujours accès
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
        return True
    
    # TODO: Implémenter la vraie logique de permissions basée sur les sessions sage-femme titulaire
    # Pour l'instant, permettre l'accès à tous les utilisateurs authentifiés
    return True


@login_required
def administration_sages_femmes_view(request):
    """
    Vue pour la gestion des sages-femmes
    """
    if not check_titulaire_permission(request):
        messages.error(request, "Accès non autorisé. Seuls les titulaires peuvent accéder à cette section.")
        return redirect('home')
    
    sagefemmes = SageFemme.objects.all().order_by('nom', 'prenom')
    
    context = {
        'page_title': 'Administration - Sages Femmes',
        'section': 'administration',
        'sagefemmes': sagefemmes
    }
    return render(request, 'core/administration/sages_femmes.html', context)


def sagefemme_list_view(request):
    """Vue HTMX pour la liste filtrée des sages-femmes"""
    if not check_titulaire_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    sagefemmes = SageFemme.objects.all().order_by('nom', 'prenom')
    
    # Filtres
    search = request.GET.get('search', '').strip()
    situation = request.GET.get('situation', '').strip()
    status = request.GET.get('status', '').strip()
    
    if search:
        sagefemmes = sagefemmes.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
    
    if situation:
        sagefemmes = sagefemmes.filter(situation=situation)
    
    # Le filtrage par statut se base maintenant sur les périodes d'activité
    # if status == 'active':
    #     sagefemmes = [sf for sf in sagefemmes if sf.est_actuellement_active]
    # elif status == 'inactive':
    #     sagefemmes = [sf for sf in sagefemmes if not sf.est_actuellement_active]
    
    context = {
        'sagefemmes': sagefemmes
    }
    return render(request, 'core/administration/partials/sagefemme_table.html', context)


@csrf_protect
def sagefemme_create_view(request):
    """Vue pour créer une sage-femme"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'POST':
            form = SageFemmeForm(request.POST)
            if form.is_valid():
                sagefemme = form.save()
                
                # Créer automatiquement une période d'activité par défaut (active depuis aujourd'hui)
                try:
                    PeriodeActivite.objects.create(
                        sage_femme=sagefemme,
                        date_debut=date.today(),
                        commentaire="Début d'activité - créé automatiquement"
                    )
                except Exception as e:
                    # Si erreur dans la création de période, on continue sans bloquer
                    print(f"Erreur création période: {e}")
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Sage-femme {sagefemme.nom_complet} créée avec succès.", "success");
                    document.getElementById('modal-container').innerHTML = '';
                    window.location.reload();
                </script>
                '''
                return response
            else:
                # Formulaire invalide, renvoyer le formulaire avec erreurs
                context = {
                    'form': form,
                    'today': date.today()
                }
                return render(request, 'core/administration/sagefemme_form.html', context)
        else:
            form = SageFemmeForm()
        
        context = {
            'form': form,
            'today': date.today()
        }
        return render(request, 'core/administration/sagefemme_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def sagefemme_detail_view(request, pk):
    """Vue pour voir les détails d'une sage-femme"""
    if not check_titulaire_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    sagefemme = get_object_or_404(
        SageFemme.objects.select_related('remplacement_de'), 
        pk=pk
    )
    # Précharger les périodes d'activité triées par date de début décroissante
    sagefemme.periodes_activite_all = sagefemme.periodes_activite.all().order_by('-date_debut')
    
    context = {
        'sagefemme': sagefemme,
        'today': date.today()
    }
    return render(request, 'core/administration/sagefemme_detail.html', context)


def sagefemme_update_view(request, pk):
    """Vue pour modifier une sage-femme"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        sagefemme = get_object_or_404(SageFemme, pk=pk)
        
        if request.method == 'POST':
            form = SageFemmeForm(request.POST, instance=sagefemme)
            if form.is_valid():
                sagefemme = form.save()
                
                # Traiter les modifications de périodes d'activité
                periodes_modifiees = []
                erreurs_periodes = []
                
                for key, value in request.POST.items():
                    if key.startswith('debut_'):
                        periode_id = key.replace('debut_', '')
                        try:
                            periode = PeriodeActivite.objects.get(pk=periode_id, sage_femme=sagefemme)
                            date_debut = datetime.strptime(value, '%Y-%m-%d').date() if value else None
                            date_fin_key = f'fin_{periode_id}'
                            date_fin_value = request.POST.get(date_fin_key, '')
                            date_fin = datetime.strptime(date_fin_value, '%Y-%m-%d').date() if date_fin_value else None
                            
                            # Mettre à jour seulement si on a une date de début valide
                            if date_debut:
                                periode.date_debut = date_debut
                                periode.date_fin = date_fin
                                periode.full_clean()  # Validation métier
                                periode.save()
                                periodes_modifiees.append(periode_id)
                            else:
                                erreurs_periodes.append(f"Date de début manquante pour période {periode_id}")
                        except PeriodeActivite.DoesNotExist:
                            erreurs_periodes.append(f"Période {periode_id} introuvable")
                        except ValueError as e:
                            erreurs_periodes.append(f"Format de date invalide pour période {periode_id}")
                        except Exception as e:
                            erreurs_periodes.append(f"Erreur période {periode_id}: {str(e)}")
                
                # Préparer le message de notification
                message_parts = [f"Sage-femme {sagefemme.nom_complet} modifiée avec succès"]
                if periodes_modifiees:
                    message_parts.append(f"{len(periodes_modifiees)} période(s) mise(s) à jour")
                if erreurs_periodes:
                    message_parts.extend(erreurs_periodes)
                
                message = ". ".join(message_parts) + "."
                notification_type = "success" if not erreurs_periodes else "warning"
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("{message}", "{notification_type}");
                    document.getElementById('modal-container').innerHTML = '';
                    window.location.reload();
                </script>
                '''
                return response
            else:
                # Formulaire invalide, renvoyer le formulaire avec erreurs
                context = {
                    'form': form,
                    'sagefemme': sagefemme,
                    'today': date.today()
                }
                return render(request, 'core/administration/sagefemme_form.html', context)
        else:
            form = SageFemmeForm(instance=sagefemme)
        
        context = {
            'form': form,
            'sagefemme': sagefemme,
            'today': date.today()
        }
        return render(request, 'core/administration/sagefemme_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def sagefemme_delete_view(request, pk):
    """Vue pour supprimer une sage-femme"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'DELETE':
            sagefemme = get_object_or_404(SageFemme, pk=pk)
            nom_complet = sagefemme.nom_complet
            sagefemme.delete()
            
            # Retourner une réponse vide pour que HTMX supprime la ligne
            response = HttpResponse()
            response.content = f'''
            <script>
                window.showNotification("Sage-femme {nom_complet} supprimée avec succès.", "success");
            </script>
            '''
            return response
        
        return HttpResponse("Méthode non autorisée", status=405)
    
    except Http404:
        return HttpResponse("Sage-femme introuvable", status=404)
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


# Les fonctions d'activation/désactivation ne sont plus nécessaires
# Le statut est maintenant géré uniquement via les périodes d'activité


@require_http_methods(["POST"])
def ajouter_periode_activite_view(request, pk):
    """Vue API pour ajouter une période d'activité"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        sagefemme = get_object_or_404(SageFemme, pk=pk)
        data = json.loads(request.body)
        
        date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        date_fin = None
        if data.get('date_fin'):
            date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        # Créer la période d'activité
        periode = PeriodeActivite(
            sage_femme=sagefemme,
            date_debut=date_debut,
            date_fin=date_fin,
            commentaire=data.get('commentaire', '')
        )
        
        # Valider avant de sauvegarder
        periode.full_clean()
        periode.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Période d\'activité ajoutée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Sage-femme introuvable'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def modifier_periode_activite_view(request, pk):
    """Vue API pour modifier une période d'activité"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        periode = get_object_or_404(PeriodeActivite, pk=pk)
        data = json.loads(request.body)
        
        # Modifier les champs fournis
        if 'date_debut' in data:
            if data['date_debut']:
                periode.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            
        if 'date_fin' in data:
            if data['date_fin']:
                periode.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            else:
                periode.date_fin = None
                
        if 'commentaire' in data:
            periode.commentaire = data['commentaire'] or ''
        
        # Valider et sauvegarder
        periode.full_clean()
        periode.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Période modifiée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Période introuvable'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Format de date invalide'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["DELETE"])
def supprimer_periode_activite_view(request, pk):
    """Vue API pour supprimer une période d'activité"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        periode = get_object_or_404(PeriodeActivite, pk=pk)
        periode.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Période supprimée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Période introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def terminer_periode_activite_view(request, pk):
    """Vue API pour terminer une période d'activité (ancienne fonction conservée)"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        periode = get_object_or_404(PeriodeActivite, pk=pk)
        
        # Terminer la période à la date d'aujourd'hui
        from django.utils import timezone
        periode.date_fin = timezone.now().date()
        periode.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Période terminée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Période introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


