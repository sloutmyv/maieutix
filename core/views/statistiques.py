"""
Views pour les statistiques
Logique métier pour l'analyse et le reporting
"""

from django.shortcuts import render


def statistiques_view(request):
    """
    Vue principale pour les statistiques
    """
    context = {
        'page_title': 'Statistiques',
        'section': 'statistiques'
    }
    return render(request, 'core/statistiques/index.html', context)


def rapport_mensuel_view(request):
    """
    Vue pour le rapport mensuel
    """
    context = {
        'page_title': 'Rapport Mensuel'
    }
    return render(request, 'core/statistiques/rapport_mensuel.html', context)


def analyse_activite_view(request):
    """
    Vue pour l'analyse d'activité
    """
    context = {
        'page_title': 'Analyse d\'Activité'
    }
    return render(request, 'core/statistiques/analyse.html', context)