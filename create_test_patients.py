#!/usr/bin/env python
"""
Script pour créer des données de test pour les patients
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Configuration Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maieutix.settings')
django.setup()

from core.models import Patient, Caisse

def create_test_patients():
    # Récupérer ou créer une caisse
    caisse, created = Caisse.objects.get_or_create(nom='CAFAT')
    if created:
        print(f"Caisse créée: {caisse.nom}")
    
    # Supprimer les patients existants pour éviter les doublons
    Patient.objects.all().delete()
    print("Patients existants supprimés")
    
    # Créer 10 patientes femmes
    femmes_data = [
        {'nom': 'Martin', 'prenom': 'Sophie', 'nom_jf': 'Dubois', 'profession': 'Infirmière', 'telephone': '0687123456'},
        {'nom': 'Leroy', 'prenom': 'Marie', 'nom_jf': 'Bernard', 'profession': 'Enseignante', 'telephone': '0698234567'},
        {'nom': 'Moreau', 'prenom': 'Claire', 'nom_jf': None, 'profession': 'Comptable', 'telephone': '0612345678'},
        {'nom': 'Simon', 'prenom': 'Anne', 'nom_jf': 'Petit', 'profession': 'Médecin', 'telephone': '0623456789'},
        {'nom': 'Michel', 'prenom': 'Julie', 'nom_jf': 'Durand', 'profession': None, 'telephone': '0634567890'},
        {'nom': 'Garcia', 'prenom': 'Laura', 'nom_jf': None, 'profession': 'Avocate', 'telephone': '0645678901'},
        {'nom': 'Roux', 'prenom': 'Emma', 'nom_jf': 'Morel', 'profession': 'Pharmacienne', 'telephone': '0656789012'},
        {'nom': 'David', 'prenom': 'Camille', 'nom_jf': 'Fournier', 'profession': 'Architecte', 'telephone': '0667890123'},
        {'nom': 'Bertrand', 'prenom': 'Léa', 'nom_jf': None, 'profession': 'Journaliste', 'telephone': '0678901234'},
        {'nom': 'Thomas', 'prenom': 'Sarah', 'nom_jf': 'Girard', 'profession': 'Psychologue', 'telephone': '0689012345'}
    ]
    
    femmes = []
    for i, data in enumerate(femmes_data):
        # Âge entre 20 et 40 ans
        age = random.randint(20, 40)
        date_naissance = date.today() - timedelta(days=age*365 + random.randint(0, 365))
        
        # Quelques femmes enceintes
        date_grossesse = None
        if i in [0, 2, 5, 7]:  # 4 femmes enceintes
            date_grossesse = date.today() - timedelta(days=random.randint(30, 280))
        
        # Certaines assurées par un tiers
        if i in [1, 4, 6, 8]:  # 4 femmes ayant-droit
            patient = Patient.objects.create(
                type_patient='femme',
                nom=data['nom'],
                prenom=data['prenom'],
                date_naissance=date_naissance,
                nom_jf=data['nom_jf'],
                profession=data['profession'],
                telephone=data['telephone'],
                date_debut_grossesse=date_grossesse,
                est_assure_titulaire=False,
                nom_assure=f'Pierre {data["nom"]}',
                prenom_assure='Pierre',
                date_naissance_assure=date_naissance - timedelta(days=random.randint(365, 3650)),
                rue_assure=f'{random.randint(1, 100)} rue des Exemples',
                code_postal_assure=f'{random.randint(98800, 98890)}',
                commune_assure='Nouméa',
                caisse=caisse
            )
        else:  # Assurées titulaires
            patient = Patient.objects.create(
                type_patient='femme',
                nom=data['nom'],
                prenom=data['prenom'],
                date_naissance=date_naissance,
                nom_jf=data['nom_jf'],
                profession=data['profession'],
                telephone=data['telephone'],
                date_debut_grossesse=date_grossesse,
                est_assure_titulaire=True,
                caisse=caisse
            )
        
        femmes.append(patient)
        print(f'Femme créée: {patient.nom_complet} - {"Titulaire" if patient.est_assure_titulaire else "Ayant-droit"}')
    
    # Créer des bébés
    bebes_data = [
        {'nom': 'Martin', 'prenom': 'Lucas'},
        {'nom': 'Martin', 'prenom': 'Emma'},  # Jumeaux pour Sophie Martin
        {'nom': 'Leroy', 'prenom': 'Noah'},
        {'nom': 'Moreau', 'prenom': 'Léo'},
        {'nom': 'Simon', 'prenom': 'Chloé'},
        {'nom': 'Michel', 'prenom': 'Hugo'},
        {'nom': 'Garcia', 'prenom': 'Zoé'},
    ]
    
    # Utiliser les 6 premières femmes comme mères
    meres = femmes[:6]
    
    for i, data in enumerate(bebes_data):
        mere = meres[i % len(meres)]  # Assigner une mère
        
        # Âge entre 0 et 3 ans
        age_jours = random.randint(0, 3*365)
        date_naissance = date.today() - timedelta(days=age_jours)
        
        # Les bébés ont la même assurance que leur mère
        if mere.est_assure_titulaire:
            bebe = Patient.objects.create(
                type_patient='bebe',
                nom=data['nom'],
                prenom=data['prenom'],
                date_naissance=date_naissance,
                mere=mere,
                est_assure_titulaire=True,
                caisse=mere.caisse
            )
        else:
            bebe = Patient.objects.create(
                type_patient='bebe',
                nom=data['nom'],
                prenom=data['prenom'],
                date_naissance=date_naissance,
                mere=mere,
                est_assure_titulaire=False,
                nom_assure=mere.nom_assure,
                prenom_assure=mere.prenom_assure,
                date_naissance_assure=mere.date_naissance_assure,
                rue_assure=mere.rue_assure,
                code_postal_assure=mere.code_postal_assure,
                commune_assure=mere.commune_assure,
                caisse=mere.caisse
            )
        
        print(f'Bébé créé: {bebe.nom_complet} - Mère: {mere.nom_complet}')
    
    print(f'\n=== RÉSUMÉ ===')
    print(f'Total patients: {Patient.objects.count()}')
    print(f'Femmes: {Patient.objects.filter(type_patient="femme").count()}')
    print(f'Bébés: {Patient.objects.filter(type_patient="bebe").count()}')
    print(f'Assurés titulaires: {Patient.objects.filter(est_assure_titulaire=True).count()}')
    print(f'Ayants-droit: {Patient.objects.filter(est_assure_titulaire=False).count()}')

if __name__ == '__main__':
    create_test_patients()