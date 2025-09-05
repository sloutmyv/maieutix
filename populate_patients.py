#!/usr/bin/env python3
"""
Script pour ajouter 10 patientes et 5 bébés à la base de données
en respectant les contraintes métier du modèle Patient.
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maieutix.settings')
django.setup()

from core.models.patient import Patient
from core.models.caisse import Caisse

def create_patients():
    """Crée 10 patientes avec des données réalistes"""
    
    # Récupérer les caisses disponibles
    caisses = list(Caisse.objects.all())
    if not caisses:
        print("Aucune caisse trouvée. Assurez-vous d'avoir des caisses en base.")
        return []
    
    # Données réalistes pour les patientes
    patientes_data = [
        {
            'nom': 'Martin',
            'prenom': 'Sophie',
            'nom_jf': 'Dubois',
            'profession': 'Infirmière',
            'telephone': '0687123456',
            'numero_ep': 'EP001234',
            'age': 28,
            'debut_grossesse_il_y_a_jours': 180,  # 6 mois de grossesse
        },
        {
            'nom': 'Leroy',
            'prenom': 'Marie',
            'nom_jf': 'Petit',
            'profession': 'Enseignante',
            'telephone': '0698765432',
            'numero_ep': 'EP002345',
            'age': 32,
            'debut_grossesse_il_y_a_jours': 120,  # 4 mois de grossesse
        },
        {
            'nom': 'Durand',
            'prenom': 'Julie',
            'nom_jf': 'Moreau',
            'profession': 'Comptable',
            'telephone': '0612345678',
            'numero_ep': 'EP003456',
            'age': 25,
            'debut_grossesse_il_y_a_jours': 220,  # 7 mois de grossesse
        },
        {
            'nom': 'Bernard',
            'prenom': 'Anne',
            'nom_jf': 'Simon',
            'profession': 'Secrétaire',
            'telephone': '0623456789',
            'numero_ep': 'EP004567',
            'age': 30,
            'debut_grossesse_il_y_a_jours': 90,   # 3 mois de grossesse
        },
        {
            'nom': 'Thomas',
            'prenom': 'Claire',
            'nom_jf': 'Laurent',
            'profession': 'Pharmacienne',
            'telephone': '0634567890',
            'numero_ep': 'EP005678',
            'age': 35,
            'debut_grossesse_il_y_a_jours': 160,  # 5.5 mois de grossesse
        },
        {
            'nom': 'Robert',
            'prenom': 'Isabelle',
            'nom_jf': 'Michel',
            'profession': 'Avocate',
            'telephone': '0645678901',
            'numero_ep': 'EP006789',
            'age': 33,
            'debut_grossesse_il_y_a_jours': 140,  # 5 mois de grossesse
        },
        {
            'nom': 'Richard',
            'prenom': 'Nathalie',
            'nom_jf': 'Garcia',
            'profession': 'Médecin',
            'telephone': '0656789012',
            'numero_ep': 'EP007890',
            'age': 29,
            'debut_grossesse_il_y_a_jours': 200,  # 6.5 mois de grossesse
        },
        {
            'nom': 'Petit',
            'prenom': 'Céline',
            'nom_jf': 'Martinez',
            'profession': 'Kinésithérapeute',
            'telephone': '0667890123',
            'numero_ep': 'EP008901',
            'age': 27,
            'debut_grossesse_il_y_a_jours': 110,  # 3.5 mois de grossesse
        },
        {
            'nom': 'Dubois',
            'prenom': 'Valérie',
            'nom_jf': 'Rodriguez',
            'profession': 'Psychologue',
            'telephone': '0678901234',
            'numero_ep': 'EP009012',
            'age': 31,
            'debut_grossesse_il_y_a_jours': 170,  # 6 mois de grossesse
        },
        {
            'nom': 'Moreau',
            'prenom': 'Sandrine',
            'nom_jf': 'Lopez',
            'profession': 'Architecte',
            'telephone': '0689012345',
            'numero_ep': 'EP010123',
            'age': 26,
            'debut_grossesse_il_y_a_jours': 130,  # 4.5 mois de grossesse
        }
    ]
    
    patientes_creees = []
    
    for i, data in enumerate(patientes_data):
        # Calcul des dates
        date_naissance = date.today() - timedelta(days=data['age'] * 365.25)
        date_debut_grossesse = date.today() - timedelta(days=data['debut_grossesse_il_y_a_jours'])
        
        # Création de la patiente
        patiente = Patient(
            type_patient='femme',
            nom=data['nom'],
            prenom=data['prenom'],
            date_naissance=date_naissance,
            nom_jf=data['nom_jf'],
            profession=data['profession'],
            telephone=data['telephone'],
            numero_ep=data['numero_ep'],
            date_debut_grossesse=date_debut_grossesse,
            est_assure_titulaire=True,
            caisse=random.choice(caisses),
            is_active=True
        )
        
        # Validation et sauvegarde
        try:
            patiente.full_clean()
            patiente.save()
            patientes_creees.append(patiente)
            print(f"✓ Patiente créée: {patiente.nom_complet} (grossesse: {patiente.age_grossesse})")
        except Exception as e:
            print(f"✗ Erreur lors de la création de {data['prenom']} {data['nom']}: {e}")
    
    return patientes_creees

def create_bebes(patientes):
    """Crée 5 bébés liés aux patientes"""
    
    if len(patientes) < 5:
        print(f"Pas assez de patientes ({len(patientes)}) pour créer 5 bébés")
        return []
    
    # Sélectionner 5 patientes au hasard pour les bébés
    meres = random.sample(patientes, 5)
    
    # Données pour les bébés
    prenoms_bebes = ['Lucas', 'Emma', 'Gabriel', 'Chloé', 'Nathan']
    
    bebes_crees = []
    
    for i, mere in enumerate(meres):
        # Le bébé prend le nom de la mère
        # Date de naissance récente (entre 0 et 30 jours)
        jours_depuis_naissance = random.randint(0, 30)
        date_naissance_bebe = date.today() - timedelta(days=jours_depuis_naissance)
        
        bebe = Patient(
            type_patient='bebe',
            nom=mere.nom,  # Même nom que la mère
            prenom=prenoms_bebes[i],
            date_naissance=date_naissance_bebe,
            mere=mere,
            est_assure_titulaire=False,  # Un bébé ne peut pas être assuré titulaire
            # Informations de l'assuré titulaire (la mère)
            nom_assure=mere.nom,
            prenom_assure=mere.prenom,
            date_naissance_assure=mere.date_naissance,
            rue_assure="123 Rue de la Maternité",
            code_postal_assure="98800",
            commune_assure="Nouméa",
            caisse=mere.caisse,  # Même caisse que la mère
            is_active=True
        )
        
        # Validation et sauvegarde
        try:
            bebe.full_clean()
            bebe.save()
            bebes_crees.append(bebe)
            print(f"✓ Bébé créé: {bebe.nom_complet} (âge: {bebe.age_detail}, mère: {mere.nom_complet})")
        except Exception as e:
            print(f"✗ Erreur lors de la création du bébé {prenoms_bebes[i]}: {e}")
    
    return bebes_crees

def main():
    print("🏥 Début du peuplement de la base de données avec des patients...")
    print()
    
    # Compter les patients existants
    patients_existants = Patient.objects.count()
    print(f"📊 Patients existants en base: {patients_existants}")
    print()
    
    # Créer les patientes
    print("👩 Création de 10 patientes...")
    patientes = create_patients()
    print(f"✅ {len(patientes)} patientes créées avec succès")
    print()
    
    # Créer les bébés
    print("👶 Création de 5 bébés...")
    bebes = create_bebes(patientes)
    print(f"✅ {len(bebes)} bébés créés avec succès")
    print()
    
    # Statistiques finales
    total_patients = Patient.objects.count()
    femmes = Patient.objects.filter(type_patient='femme').count()
    bebes_total = Patient.objects.filter(type_patient='bebe').count()
    
    print("📈 Statistiques finales:")
    print(f"  - Total patients en base: {total_patients}")
    print(f"  - Femmes: {femmes}")
    print(f"  - Bébés: {bebes_total}")
    print()
    
    print("🎉 Peuplement terminé avec succès!")

if __name__ == "__main__":
    main()