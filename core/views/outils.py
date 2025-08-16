"""
Views pour les outils
Logique métier pour les fonctionnalités utilitaires
"""

from django.shortcuts import render


def outils_view(request):
    """
    Vue principale pour les outils
    """
    context = {
        'page_title': 'Outils',
        'section': 'outils'
    }
    return render(request, 'core/outils/index.html', context)


def calculatrice_view(request):
    """
    Vue pour les outils de calcul
    """
    context = {
        'page_title': 'Calculatrice'
    }
    return render(request, 'core/outils/calculatrice.html', context)


def references_view(request):
    """
    Vue pour les références médicales
    """
    context = {
        'page_title': 'Références Médicales'
    }
    return render(request, 'core/outils/references.html', context)