"""
Views pour la gestion des feuilles de soins
Logique métier et interactions pour les consultations
"""

from django.shortcuts import render


def home_view(request):
    """
    Vue pour la page d'accueil - redirige vers feuille de soins
    """
    return feuille_soins_view(request)


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


def nouvelle_consultation_view(request):
    """
    Vue pour créer une nouvelle consultation
    """
    context = {
        'page_title': 'Nouvelle Consultation'
    }
    return render(request, 'core/feuille_soins/nouvelle.html', context)


def recherche_consultation_view(request):
    """
    Vue pour rechercher dans les consultations
    """
    context = {
        'page_title': 'Recherche Consultations'
    }
    return render(request, 'core/feuille_soins/recherche.html', context)


def historique_consultation_view(request):
    """
    Vue pour l'historique des consultations
    """
    context = {
        'page_title': 'Historique Consultations'
    }
    return render(request, 'core/feuille_soins/historique.html', context)