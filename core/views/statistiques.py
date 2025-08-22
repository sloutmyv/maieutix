"""
Views pour les statistiques
Logique métier pour l'analyse et le reporting
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def statistiques_view(request):
    """
    Vue principale pour les statistiques
    """
    context = {
        'page_title': 'Statistiques',
        'section': 'statistiques'
    }
    return render(request, 'core/statistiques/index.html', context)


