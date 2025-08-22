"""
Views pour la gestion des feuilles de soins
Logique métier et interactions pour les consultations
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home_view(request):
    """
    Vue pour la page d'accueil
    """
    context = {
        'page_title': 'Accueil'
    }
    return render(request, 'core/home.html', context)


@login_required
def feuille_soins_view(request):
    """
    Vue principale pour la gestion des feuilles de soins
    Affiche le tableau de bord des consultations
    """
    context = {
        'page_title': 'Feuille de Soins',
        'consultations_recentes': [
            {
                'date': '15/08/2025',
                'patiente': 'Marie Dupont',
                'type': 'Consultation prénatale',
                'statut': 'complete',
                'statut_label': 'Complète'
            },
            {
                'date': '14/08/2025', 
                'patiente': 'Sophie Martin',
                'type': 'Suivi grossesse',
                'statut': 'en_cours',
                'statut_label': 'En cours'
            },
            {
                'date': '13/08/2025',
                'patiente': 'Léa Dubois', 
                'type': 'Consultation postnatale',
                'statut': 'complete',
                'statut_label': 'Complète'
            }
        ]
    }
    return render(request, 'core/feuille_soins.html', context)


