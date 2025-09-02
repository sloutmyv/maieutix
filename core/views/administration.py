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
from core.models.acte import Acte, TarifPeriode
from core.models.cadre_exercice import CadreExercice
from core.models.prestation import Prestation
from core.models.caisse import Caisse
from core.models.condition_paiement import ConditionPaiement


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
    """Vérifie si l'utilisateur a les permissions d'administration complètes (titulaire ou superuser)"""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return False
    
    # Super admin a toujours accès
    if request.user.is_superuser:
        return True
    
    # Vérifier si l'utilisateur est une sage-femme titulaire
    try:
        return hasattr(request.user, 'sagefemme') and request.user.sagefemme.situation == 'titulaire'
    except:
        return False


def check_administration_read_permission(request):
    """Vérifie si l'utilisateur a les permissions de lecture en administration (titulaire, collaborateur, remplaçant ou superuser)"""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return False
    
    # Super admin a toujours accès
    if request.user.is_superuser:
        return True
    
    # Vérifier si l'utilisateur est une sage-femme (titulaire, collaborateur ou remplaçant)
    try:
        if hasattr(request.user, 'sagefemme'):
            situation = request.user.sagefemme.situation
            return situation in ['titulaire', 'collaborateur', 'remplacant']
        return False
    except:
        return False


@login_required
def administration_sages_femmes_view(request):
    """
    Vue pour la gestion des sages-femmes
    """
    if not check_administration_read_permission(request):
        messages.error(request, "Accès non autorisé.")
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
                
                # Créer automatiquement un compte utilisateur pour la sage-femme
                try:
                    sagefemme.creer_compte_utilisateur()
                except Exception as e:
                    print(f"Erreur création compte utilisateur: {e}")
                
                # Créer automatiquement une période d'activité par défaut (active depuis aujourd'hui)
                try:
                    PeriodeActivite.objects.create(
                        sage_femme=sagefemme,
                        date_debut=date.today(),
                        commentaire=""
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
    if not check_administration_read_permission(request):
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
                
                # Créer un compte utilisateur si il n'existe pas déjà
                if not sagefemme.user:
                    try:
                        sagefemme.creer_compte_utilisateur()
                    except Exception as e:
                        print(f"Erreur création compte utilisateur: {e}")
                
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


# ============================================================================
# VUES POUR LA GESTION DES ACTES MEDICAUX
# ============================================================================

class ActeForm(ModelForm):
    """Formulaire pour les actes médicaux"""
    
    class Meta:
        model = Acte
        fields = ['code', 'libelle']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Ex: CSF, VGC...'
            }),
            'libelle': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 2,
                'placeholder': 'Description complète de l\'acte...'
            })
        }

    def clean_code(self):
        """Valide l'unicité du code"""
        code = self.cleaned_data.get('code')
        if code:
            queryset = Acte.objects.filter(code__iexact=code)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Un acte avec ce code existe déjà.")
        return code.upper() if code else code


class TarifPeriodeForm(ModelForm):
    """Formulaire pour les périodes tarifaires"""
    
    class Meta:
        model = TarifPeriode
        fields = ['acte', 'cout_xpf', 'date_debut', 'date_fin']
        widgets = {
            'acte': forms.Select(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'cout_xpf': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Montant en XPF'
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            })
        }


@login_required
def administration_actes_view(request):
    """
    Vue pour la gestion des actes médicaux
    """
    if not check_administration_read_permission(request):
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    actes = Acte.objects.all().order_by('code')
    
    context = {
        'page_title': 'Administration - Actes',
        'section': 'administration',
        'actes': actes
    }
    return render(request, 'core/administration/actes.html', context)


def acte_list_view(request):
    """Vue HTMX pour la liste filtrée des actes"""
    if not check_titulaire_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    actes = Acte.objects.all().order_by('code')
    
    # Filtres
    search = request.GET.get('search', '').strip()
    
    if search:
        actes = actes.filter(
            Q(code__icontains=search) |
            Q(libelle__icontains=search)
        )
    
    context = {
        'actes': actes
    }
    return render(request, 'core/administration/partials/acte_table.html', context)


@csrf_protect
def acte_create_view(request):
    """Vue pour créer un acte"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'POST':
            form = ActeForm(request.POST)
            if form.is_valid():
                acte = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Acte {acte.code} créé avec succès.", "success");
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
                return render(request, 'core/administration/acte_form.html', context)
        else:
            form = ActeForm()
        
        context = {
            'form': form,
            'today': date.today()
        }
        return render(request, 'core/administration/acte_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def acte_detail_view(request, pk):
    """Vue pour voir les détails d'un acte"""
    if not check_administration_read_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    acte = get_object_or_404(Acte, pk=pk)
    # Précharger les périodes tarifaires triées par date de début décroissante
    acte.tarifs_periodes_all = acte.tarifs_periodes.all().order_by('-date_debut')
    
    context = {
        'acte': acte,
        'today': date.today()
    }
    return render(request, 'core/administration/acte_detail.html', context)


def acte_update_view(request, pk):
    """Vue pour modifier un acte"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        acte = get_object_or_404(Acte, pk=pk)
        # Précharger les périodes tarifaires triées par date de début décroissante
        acte.tarifs_periodes_all = acte.tarifs_periodes.all().order_by('-date_debut')
        
        if request.method == 'POST':
            form = ActeForm(request.POST, instance=acte)
            if form.is_valid():
                acte = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Acte {acte.code} modifié avec succès.", "success");
                    document.getElementById('modal-container').innerHTML = '';
                    window.location.reload();
                </script>
                '''
                return response
            else:
                # Formulaire invalide, renvoyer le formulaire avec erreurs
                context = {
                    'form': form,
                    'acte': acte,
                    'today': date.today()
                }
                return render(request, 'core/administration/acte_form.html', context)
        else:
            form = ActeForm(instance=acte)
            # S'assurer que les périodes tarifaires sont chargées pour le rendu du formulaire
            acte.tarifs_periodes_all = acte.tarifs_periodes.all().order_by('-date_debut')
        
        context = {
            'form': form,
            'acte': acte,
            'today': date.today()
        }
        return render(request, 'core/administration/acte_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def acte_delete_view(request, pk):
    """Vue pour supprimer un acte"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'DELETE':
            acte = get_object_or_404(Acte, pk=pk)
            code = acte.code
            acte.delete()
            
            # Retourner une réponse vide pour que HTMX supprime la ligne
            response = HttpResponse()
            response.content = f'''
            <script>
                window.showNotification("Acte {code} supprimé avec succès.", "success");
            </script>
            '''
            return response
        
        return HttpResponse("Méthode non autorisée", status=405)
    
    except Http404:
        return HttpResponse("Acte introuvable", status=404)
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


@require_http_methods(["POST"])
def ajouter_tarif_periode_view(request, pk):
    """Vue API pour ajouter une période tarifaire"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        acte = get_object_or_404(Acte, pk=pk)
        data = json.loads(request.body)
        
        cout_xpf = data['cout_xpf']
        date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
        date_fin = None
        if data.get('date_fin'):
            date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
        
        # Créer la période tarifaire
        tarif_periode = TarifPeriode(
            acte=acte,
            cout_xpf=cout_xpf,
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        # Valider avant de sauvegarder
        tarif_periode.full_clean()
        tarif_periode.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Période tarifaire ajoutée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Acte introuvable'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Données invalides'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def modifier_tarif_periode_view(request, pk):
    """Vue API pour modifier une période tarifaire"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        tarif_periode = get_object_or_404(TarifPeriode, pk=pk)
        data = json.loads(request.body)
        
        # Modifier les champs fournis
        if 'cout_xpf' in data:
            tarif_periode.cout_xpf = data['cout_xpf']
            
        if 'date_debut' in data:
            if data['date_debut']:
                tarif_periode.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            
        if 'date_fin' in data:
            if data['date_fin']:
                tarif_periode.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            else:
                tarif_periode.date_fin = None
        
        # Valider et sauvegarder
        tarif_periode.full_clean()
        tarif_periode.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Période tarifaire modifiée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Période tarifaire introuvable'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Données invalides'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["DELETE"])
def supprimer_tarif_periode_view(request, pk):
    """Vue API pour supprimer une période tarifaire"""
    if not check_titulaire_permission(request):
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    try:
        tarif_periode = get_object_or_404(TarifPeriode, pk=pk)
        tarif_periode.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Période tarifaire supprimée avec succès'
        })
        
    except Http404:
        return JsonResponse({'success': False, 'error': 'Période tarifaire introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================================================
# VUES POUR LA GESTION DES PRESTATIONS
# ============================================================================

class PrestationForm(ModelForm):
    """Formulaire pour les prestations"""
    
    class Meta:
        model = Prestation
        fields = [
            'cadre_exercice', 'designation', 'suffixe', 'origine', 'prescription',
            'limite', 'acte', 'cotation', 'entente_prealable', 'assurance_maladie', 
            'assurance_maternite_normale', 'assurance_maternite_pathologie', 'observation'
        ]
        widgets = {
            'cadre_exercice': forms.Select(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'designation': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 2,
                'placeholder': 'Description de la prestation...'
            }),
            'limite': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 3,
                'placeholder': 'Limites ou contraintes (optionnel)...'
            }),
            'acte': forms.Select(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'cotation': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'step': '0.01',
                'placeholder': 'Ex: 25.50'
            }),
            'entente_prealable': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Conditions d\'entente préalable...'
            }),
            'assurance_maladie': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Informations assurance maladie (optionnel)...'
            }),
            'assurance_maternite_normale': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Informations maternité normale (optionnel)...'
            }),
            'assurance_maternite_pathologie': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Informations maternité pathologie (optionnel)...'
            }),
            'observation': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 3,
                'placeholder': 'Observations particulières (optionnel)...'
            }),
            'suffixe': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Suffixe (optionnel)...'
            }),
            'origine': forms.Select(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'prescription': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary'
            })
        }

    def clean_cotation(self):
        """Valide que la cotation est positive"""
        cotation = self.cleaned_data.get('cotation')
        if cotation and cotation <= 0:
            raise forms.ValidationError("La cotation doit être un nombre positif.")
        return cotation


@login_required
def administration_prestations_view(request):
    """
    Vue pour la gestion des prestations
    """
    if not check_administration_read_permission(request):
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    prestations = Prestation.objects.select_related('cadre_exercice', 'acte').filter(actif=True).order_by('cadre_exercice__label', 'designation')
    cadres_exercice = CadreExercice.objects.all().order_by('label')
    actes = Acte.objects.all().order_by('code')
    
    context = {
        'page_title': 'Administration - Prestations',
        'section': 'administration',
        'prestations': prestations,
        'cadres_exercice': cadres_exercice,
        'actes': actes
    }
    return render(request, 'core/administration/prestations.html', context)


def prestation_list_view(request):
    """Vue HTMX pour la liste filtrée des prestations"""
    if not check_titulaire_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    prestations = Prestation.objects.select_related('cadre_exercice', 'acte').filter(actif=True).order_by('cadre_exercice__label', 'designation')
    
    # Filtres
    search = request.GET.get('search', '').strip()
    cadre_exercice = request.GET.get('cadre_exercice', '').strip()
    acte_filter = request.GET.get('acte', '').strip()
    
    if search:
        prestations = prestations.filter(
            Q(designation__icontains=search) |
            Q(suffixe__icontains=search) |
            Q(limite__icontains=search) |
            Q(cadre_exercice__label__icontains=search) |
            Q(acte__code__icontains=search) |
            Q(acte__libelle__icontains=search)
        )
    
    if cadre_exercice:
        try:
            cadre_exercice = int(cadre_exercice)
            prestations = prestations.filter(cadre_exercice_id=cadre_exercice)
        except (ValueError, TypeError):
            pass  # Ignorer les valeurs non numériques
        
    if acte_filter:
        try:
            acte_filter = int(acte_filter)
            prestations = prestations.filter(acte_id=acte_filter)
        except (ValueError, TypeError):
            pass  # Ignorer les valeurs non numériques
    
    context = {
        'prestations': prestations
    }
    return render(request, 'core/administration/partials/prestation_table.html', context)


@csrf_protect
def prestation_create_view(request):
    """Vue pour créer une prestation"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'POST':
            form = PrestationForm(request.POST)
            if form.is_valid():
                prestation = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Prestation créée avec succès.", "success");
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
                return render(request, 'core/administration/prestation_form.html', context)
        else:
            form = PrestationForm()
        
        context = {
            'form': form,
            'today': date.today()
        }
        return render(request, 'core/administration/prestation_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def prestation_detail_view(request, pk):
    """Vue pour voir les détails d'une prestation"""
    if not check_administration_read_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    prestation = get_object_or_404(
        Prestation.objects.select_related('cadre_exercice', 'acte'), 
        pk=pk
    )
    
    context = {
        'prestation': prestation,
        'today': date.today()
    }
    return render(request, 'core/administration/prestation_detail.html', context)


def prestation_update_view(request, pk):
    """Vue pour modifier une prestation"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        prestation = get_object_or_404(Prestation, pk=pk)
        
        if request.method == 'POST':
            form = PrestationForm(request.POST, instance=prestation)
            if form.is_valid():
                prestation = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et afficher notification
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Prestation modifiée avec succès.", "success");
                    document.getElementById('modal-container').innerHTML = '';
                    window.location.reload();
                </script>
                '''
                return response
            else:
                # Formulaire invalide, renvoyer le formulaire avec erreurs
                context = {
                    'form': form,
                    'prestation': prestation,
                    'today': date.today()
                }
                return render(request, 'core/administration/prestation_form.html', context)
        else:
            form = PrestationForm(instance=prestation)
        
        context = {
            'form': form,
            'prestation': prestation,
            'today': date.today()
        }
        return render(request, 'core/administration/prestation_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def prestation_delete_view(request, pk):
    """Vue pour supprimer une prestation"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'DELETE':
            prestation = get_object_or_404(Prestation, pk=pk)
            designation_courte = prestation.designation[:50] + "..." if len(prestation.designation) > 50 else prestation.designation
            prestation.delete()
            
            # Retourner une réponse vide pour que HTMX supprime la ligne
            response = HttpResponse()
            response.content = f'''
            <script>
                window.showNotification("Prestation supprimée avec succès.", "success");
            </script>
            '''
            return response
        
        return HttpResponse("Méthode non autorisée", status=405)
    
    except Http404:
        return HttpResponse("Prestation introuvable", status=404)
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


# ============================================================================
# VUES POUR LA GESTION DES CAISSES
# ============================================================================

class CaisseForm(ModelForm):
    """Formulaire pour les caisses"""
    
    class Meta:
        model = Caisse
        fields = ['nom', 'conditions_paiement_eligibles']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Nom de la caisse...'
            }),
            'conditions_paiement_eligibles': forms.CheckboxSelectMultiple(attrs={
                'class': 'text-primary focus:ring-primary'
            })
        }

    def clean_nom(self):
        """Valide l'unicité du nom"""
        nom = self.cleaned_data.get('nom')
        if nom:
            queryset = Caisse.objects.filter(nom__iexact=nom)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Une caisse avec ce nom existe déjà.")
        return nom


class ConditionPaiementForm(ModelForm):
    """Formulaire pour les conditions de paiement"""
    
    class Meta:
        model = ConditionPaiement
        fields = ['designation', 'pourcentage']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Désignation de la condition...'
            }),
            'pourcentage': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': 'Pourcentage...'
            })
        }

    def clean_designation(self):
        """Valide l'unicité de la désignation"""
        designation = self.cleaned_data.get('designation')
        if designation:
            queryset = ConditionPaiement.objects.filter(designation__iexact=designation)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Une condition avec cette désignation existe déjà.")
        return designation


@login_required
def administration_caisses_view(request):
    """
    Vue pour la gestion des caisses
    """
    if not check_administration_read_permission(request):
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    caisses = Caisse.objects.prefetch_related('conditions_paiement_eligibles').order_by('nom')
    conditions_paiement = ConditionPaiement.objects.all().order_by('designation')
    
    context = {
        'page_title': 'Administration - Caisses',
        'section': 'administration',
        'caisses': caisses,
        'conditions_paiement': conditions_paiement
    }
    return render(request, 'core/administration/caisses.html', context)


def caisse_list_view(request):
    """Vue HTMX pour la liste filtrée des caisses"""
    if not check_administration_read_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    caisses = Caisse.objects.prefetch_related('conditions_paiement_eligibles').order_by('nom')
    
    # Filtres
    search = request.GET.get('search', '').strip()
    
    if search:
        caisses = caisses.filter(nom__icontains=search)
    
    context = {
        'caisses': caisses
    }
    return render(request, 'core/administration/partials/caisse_table.html', context)


@csrf_protect
def caisse_create_view(request):
    """Vue pour créer une caisse"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'POST':
            form = CaisseForm(request.POST)
            if form.is_valid():
                caisse = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et recharger la page
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Caisse {caisse.nom} créée avec succès.", "success");
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
                return render(request, 'core/administration/caisse_form.html', context)
        else:
            form = CaisseForm()
        
        context = {
            'form': form,
            'today': date.today()
        }
        return render(request, 'core/administration/caisse_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def caisse_detail_view(request, pk):
    """Vue pour voir les détails d'une caisse"""
    if not check_administration_read_permission(request):
        return HttpResponse("Non autorisé", status=403)
    
    caisse = get_object_or_404(
        Caisse.objects.prefetch_related('conditions_paiement_eligibles'), 
        pk=pk
    )
    
    context = {
        'caisse': caisse,
        'today': date.today()
    }
    return render(request, 'core/administration/caisse_detail.html', context)


def caisse_update_view(request, pk):
    """Vue pour modifier une caisse"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        caisse = get_object_or_404(Caisse, pk=pk)
        
        if request.method == 'POST':
            form = CaisseForm(request.POST, instance=caisse)
            if form.is_valid():
                caisse = form.save()
                
                # Retourner une réponse HTMX pour fermer la modal et recharger la page
                response = HttpResponse()
                response.content = f'''
                <script>
                    window.showNotification("Caisse {caisse.nom} modifiée avec succès.", "success");
                    document.getElementById('modal-container').innerHTML = '';
                    window.location.reload();
                </script>
                '''
                return response
            else:
                # Formulaire invalide, renvoyer le formulaire avec erreurs
                context = {
                    'form': form,
                    'caisse': caisse,
                    'today': date.today()
                }
                return render(request, 'core/administration/caisse_form.html', context)
        else:
            form = CaisseForm(instance=caisse)
        
        context = {
            'form': form,
            'caisse': caisse,
            'today': date.today()
        }
        return render(request, 'core/administration/caisse_form.html', context)
    
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)


def caisse_delete_view(request, pk):
    """Vue pour supprimer une caisse"""
    try:
        if not check_titulaire_permission(request):
            return HttpResponse("Non autorisé", status=403)
        
        if request.method == 'DELETE':
            caisse = get_object_or_404(Caisse, pk=pk)
            nom = caisse.nom
            caisse.delete()
            
            # Retourner une réponse pour recharger la page après suppression
            response = HttpResponse()
            response.content = f'''
            <script>
                window.showNotification("Caisse {nom} supprimée avec succès.", "success");
                window.location.reload();
            </script>
            '''
            return response
        
        return HttpResponse("Méthode non autorisée", status=405)
    
    except Http404:
        return HttpResponse("Caisse introuvable", status=404)
    except Exception as e:
        return HttpResponse(f"Erreur serveur: {str(e)}", status=500)

