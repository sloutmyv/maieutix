"""
Views pour les outils
Logique métier pour les fonctionnalités utilitaires
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def outils_view(request):
    """
    Vue principale pour les outils
    """
    context = {
        'page_title': 'Outils',
        'section': 'outils'
    }
    return render(request, 'core/outils/index.html', context)


