"""
Views pour l'administration
Logique métier pour la gestion administrative
"""

from django.shortcuts import render


def administration_sages_femmes_view(request):
    """
    Vue pour la gestion des sages-femmes
    """
    context = {
        'page_title': 'Administration - Sages Femmes',
        'section': 'administration'
    }
    return render(request, 'core/administration/sages_femmes.html', context)


def administration_cabinet_view(request):
    """
    Vue pour la gestion du cabinet
    """
    context = {
        'page_title': 'Administration - Cabinet'
    }
    return render(request, 'core/administration/cabinet.html', context)


def parametres_view(request):
    """
    Vue pour les paramètres généraux
    """
    context = {
        'page_title': 'Paramètres'
    }
    return render(request, 'core/administration/parametres.html', context)