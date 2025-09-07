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
from core.models import Patient, Caisse, Antecedents, FrottisCV, DonneesGrossesse


class PatientForm(ModelForm):
    """Formulaire pour les patients"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        # Limiter les dates au jour actuel (pas de dates futures)
        self.fields['date_naissance'].widget.attrs['max'] = today
        self.fields['date_debut_grossesse'].widget.attrs['max'] = today  
        self.fields['date_naissance_assure'].widget.attrs['max'] = today
        
        # Limiter les choix de mère aux femmes actives uniquement
        self.fields['mere'].queryset = Patient.objects.filter(type_patient='femme', is_active=True)
        self.fields['mere'].empty_label = "Sélectionner une mère"
        self.fields['caisse'].queryset = Caisse.objects.all()
        self.fields['caisse'].empty_label = "Sélectionner une caisse"
    
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
    


@login_required
def patients_view(request):
    """
    Vue principale pour la liste des patients avec recherche
    """
    search_query = request.GET.get('search', '')
    
    # Inclure tous les patients (actifs et inactifs)
    patients = Patient.objects.all().select_related('mere', 'caisse')
    
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
    patient = get_object_or_404(Patient, id=patient_id)
    
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
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Récupérer les données de grossesse si c'est une femme
    donnees = None
    if patient.type_patient == 'femme':
        try:
            donnees = patient.donnees_grossesse
        except DonneesGrossesse.DoesNotExist:
            donnees = None
    
    context = {
        'patient': patient,
        'bebes': patient.get_bebes() if patient.type_patient == 'femme' else None,
        'donnees': donnees,
        'page_title': f'Patient - {patient.nom_complet}',
        'section': 'patients'
    }
    
    return render(request, 'core/patients/patient_detail_page.html', context)


@login_required
def patient_detail_modal(request, patient_id):
    """
    Vue pour afficher les détails d'un patient en modal (conservée pour compatibilité)
    """
    patient = get_object_or_404(Patient, id=patient_id)
    
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
        'is_active': patient.is_active,
        'redirect': '/patients/'
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


@login_required
def patient_details_for_baby(request, patient_id):
    """
    Vue pour récupérer les détails d'une mère pour pré-remplir les infos du bébé
    """
    try:
        mere = get_object_or_404(Patient, id=patient_id, type_patient='femme')
        
        data = {
            'telephone': mere.telephone,
            'caisse_id': mere.caisse.id if mere.caisse else None,
            'nom_assure': mere.nom_assure,
            'prenom_assure': mere.prenom_assure,
            'date_naissance_assure': mere.date_naissance_assure.strftime('%Y-%m-%d') if mere.date_naissance_assure else None,
            'rue_assure': mere.rue_assure,
            'code_postal_assure': mere.code_postal_assure,
            'commune_assure': mere.commune_assure,
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)


@login_required
@require_http_methods(["GET"])
def patient_antecedents(request, patient_id):
    """
    Vue pour récupérer les antécédents d'un patient
    """
    patient = get_object_or_404(Patient, id=patient_id, type_patient='femme')
    
    try:
        antecedents = patient.antecedents
        frottis = antecedents.frottis.all()
        
        data = {
            'antecedents': {
                'taille': antecedents.taille,
                'poids': antecedents.poids,
                'medecin_traitant': antecedents.medecin_traitant,
                'gynecologue': antecedents.gynecologue,
                'allergie': antecedents.allergie,
                'asthme': antecedents.asthme,
                'raa': antecedents.raa,
                'diabete': antecedents.diabete,
                'hta': antecedents.hta,
                'epilepsie': antecedents.epilepsie,
                'infection_urinaire': antecedents.infection_urinaire,
                'atcd_medicaux_notes': antecedents.atcd_medicaux_notes,
                'atcd_obstetricaux': antecedents.atcd_obstetricaux,
                'fcv_notes': antecedents.fcv_notes,
                'atcd_fam_diabete': antecedents.atcd_fam_diabete,
                'atcd_fam_hta': antecedents.atcd_fam_hta,
                'atcd_fam_cancer_sein': antecedents.atcd_fam_cancer_sein,
                'atcd_fam_hypercholesterolemie': antecedents.atcd_fam_hypercholesterolemie,
                'atcd_fam_autre': antecedents.atcd_fam_autre,
                'atcd_chirurgicaux': antecedents.atcd_chirurgicaux,
                'contraception': antecedents.contraception,
            },
            'frottis': [
                {
                    'date_frottis': frottis_item.date_frottis.strftime('%Y-%m-%d'),
                    'resultat': frottis_item.resultat
                } for frottis_item in frottis
            ]
        }
        
        return JsonResponse(data)
        
    except Antecedents.DoesNotExist:
        return JsonResponse({
            'antecedents': None,
            'frottis': []
        })


@login_required
@require_http_methods(["POST"])
@csrf_protect
def save_antecedents(request):
    """
    Vue pour sauvegarder les antécédents d'un patient
    """
    patient_id = request.POST.get('patient_id')
    if not patient_id:
        return JsonResponse({'success': False, 'error': 'Patient ID manquant'})
    
    patient = get_object_or_404(Patient, id=patient_id, type_patient='femme')
    
    try:
        # Récupérer ou créer les antécédents
        antecedents, created = Antecedents.objects.get_or_create(patient=patient)
        
        # Données biométriques
        taille = request.POST.get('taille')
        poids = request.POST.get('poids')
        if taille:
            antecedents.taille = float(taille) if taille else None
        if poids:
            antecedents.poids = float(poids) if poids else None
        
        # Médecins
        antecedents.medecin_traitant = request.POST.get('medecin_traitant', '')
        antecedents.gynecologue = request.POST.get('gynecologue', '')
        
        # ATCD médicaux
        antecedents.allergie = request.POST.get('allergie', '')
        antecedents.asthme = request.POST.get('asthme') == 'true'
        antecedents.raa = request.POST.get('raa') == 'true'
        antecedents.diabete = request.POST.get('diabete') == 'true'
        antecedents.hta = request.POST.get('hta') == 'true'
        antecedents.epilepsie = request.POST.get('epilepsie') == 'true'
        antecedents.infection_urinaire = request.POST.get('infection_urinaire') == 'true'
        antecedents.atcd_medicaux_notes = request.POST.get('atcd_medicaux_notes', '')
        
        # ATCD obstétricaux
        antecedents.atcd_obstetricaux = request.POST.get('atcd_obstetricaux', '')
        
        # FCV
        antecedents.fcv_notes = request.POST.get('fcv_notes', '')
        
        # ATCD familiaux
        antecedents.atcd_fam_diabete = request.POST.get('atcd_fam_diabete') == 'true'
        antecedents.atcd_fam_hta = request.POST.get('atcd_fam_hta') == 'true'
        antecedents.atcd_fam_cancer_sein = request.POST.get('atcd_fam_cancer_sein') == 'true'
        antecedents.atcd_fam_hypercholesterolemie = request.POST.get('atcd_fam_hypercholesterolemie') == 'true'
        antecedents.atcd_fam_autre = request.POST.get('atcd_fam_autre', '')
        
        # ATCD chirurgicaux
        antecedents.atcd_chirurgicaux = request.POST.get('atcd_chirurgicaux', '')
        
        # Contraception
        antecedents.contraception = request.POST.get('contraception', '')
        
        antecedents.save()
        
        # Gérer les frottis
        # Supprimer les anciens frottis avant de créer les nouveaux
        antecedents.frottis.all().delete()
        
        # Créer les nouveaux frottis
        frottis_counter = 0
        while True:
            date_key = f'frottis_date_{frottis_counter}'
            resultat_key = f'frottis_resultat_{frottis_counter}'
            
            if date_key not in request.POST:
                break
                
            date_frottis = request.POST.get(date_key)
            resultat = request.POST.get(resultat_key)
            
            if date_frottis and resultat:
                FrottisCV.objects.create(
                    antecedents=antecedents,
                    date_frottis=date_frottis,
                    resultat=resultat
                )
            
            frottis_counter += 1
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
@csrf_protect
def update_ddg(request, patient_id):
    """
    Met à jour la date de début de grossesse d'une patiente via AJAX
    """
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Vérifier que c'est une femme
        if patient.type_patient != 'femme':
            return JsonResponse({'success': False, 'error': 'Seules les femmes peuvent avoir une DDG'})
        
        new_ddg = request.POST.get('date_debut_grossesse')
        
        if new_ddg:
            # Valider la date (pas dans le futur)
            from datetime import datetime
            try:
                ddg_date = datetime.strptime(new_ddg, '%Y-%m-%d').date()
                if ddg_date > date.today():
                    return JsonResponse({'success': False, 'error': 'La date de début de grossesse ne peut pas être dans le futur'})
                
                patient.date_debut_grossesse = ddg_date
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Format de date invalide'})
        else:
            # Effacer la DDG si vide
            patient.date_debut_grossesse = None
        
        patient.save()
        
        # Retourner les données mises à jour pour rafraîchir l'interface
        response_data = {
            'success': True,
            'ddg': patient.date_debut_grossesse.strftime('%Y-%m-%d') if patient.date_debut_grossesse else '',
            'ddg_display': patient.date_debut_grossesse.strftime('%d/%m/%Y') if patient.date_debut_grossesse else '',
            'age_grossesse': patient.age_grossesse if patient.date_debut_grossesse else '',
        }
        
        if patient.date_debut_grossesse:
            from datetime import timedelta
            terme = patient.date_debut_grossesse + timedelta(days=273)
            response_data['terme'] = terme.strftime('%d/%m/%Y')
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def reload_pregnancy_calendar(request, patient_id):
    """
    Recharge uniquement le calendrier de grossesse d'une patiente
    """
    patient = get_object_or_404(Patient, id=patient_id, type_patient='femme')
    
    return render(request, 'core/patients/partials/calendrier_grossesse_compact.html', {
        'patient': patient
    })


@login_required
@require_http_methods(["GET"])
def patient_donnees_grossesse(request, patient_id):
    """
    Vue pour récupérer les données de grossesse d'une patiente
    """
    patient = get_object_or_404(Patient, id=patient_id, type_patient='femme')
    
    try:
        donnees = patient.donnees_grossesse
        
        data = {
            'donnees': {
                'gestite_parite': donnees.gestite_parite,
                'facteurs_risque': donnees.facteurs_risque,
                'lieu_accouchement': donnees.lieu_accouchement,
                'gs_rh': donnees.gs_rh,
                'rai': donnees.rai,
                'ht21': donnees.ht21,
                'dpni': donnees.dpni,
                'toxo': donnees.toxo,
                'rub': donnees.rub,
                'glyc_jeun': donnees.glyc_jeun,
                'ag_hbs': donnees.ag_hbs,
                'ac_anti_hbs': donnees.ac_anti_hbs,
                'hgpo': donnees.hgpo,
                'vih': donnees.vih,
                'tpha_vdrl': donnees.tpha_vdrl,
                'hb': donnees.hb,
                'plaq': donnees.plaq,
                'pv': donnees.pv,
                'ecbu': donnees.ecbu,
            }
        }
        
        return JsonResponse(data)
        
    except DonneesGrossesse.DoesNotExist:
        return JsonResponse({
            'donnees': None
        })


@login_required
@require_http_methods(["POST"])
@csrf_protect
def save_donnees_grossesse(request):
    """
    Vue pour sauvegarder les données de grossesse d'une patiente
    """
    patient_id = request.POST.get('patient_id')
    if not patient_id:
        return JsonResponse({'success': False, 'error': 'Patient ID manquant'})
    
    patient = get_object_or_404(Patient, id=patient_id, type_patient='femme')
    
    try:
        # Récupérer ou créer les données de grossesse
        donnees, created = DonneesGrossesse.objects.get_or_create(patient=patient)
        
        # Obstétrique
        donnees.gestite_parite = request.POST.get('gestite_parite', '')
        donnees.facteurs_risque = request.POST.get('facteurs_risque', '')
        donnees.lieu_accouchement = request.POST.get('lieu_accouchement', '')
        
        # Analyses de base
        donnees.gs_rh = request.POST.get('gs_rh', '')
        donnees.rai = request.POST.get('rai', '')
        donnees.ht21 = request.POST.get('ht21', '')
        donnees.dpni = request.POST.get('dpni', '')
        
        # Sérologies
        donnees.toxo = request.POST.get('toxo', '')
        donnees.rub = request.POST.get('rub', '')
        donnees.ag_hbs = request.POST.get('ag_hbs', '')
        donnees.ac_anti_hbs = request.POST.get('ac_anti_hbs', '')
        donnees.vih = request.POST.get('vih', '')
        donnees.tpha_vdrl = request.POST.get('tpha_vdrl', '')
        
        # Analyses complémentaires
        donnees.glyc_jeun = request.POST.get('glyc_jeun', '')
        donnees.hgpo = request.POST.get('hgpo', '')
        donnees.hb = request.POST.get('hb', '')
        donnees.plaq = request.POST.get('plaq', '')
        donnees.pv = request.POST.get('pv', '')
        donnees.ecbu = request.POST.get('ecbu', '')
        
        donnees.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


