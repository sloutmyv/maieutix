"""
Views pour la gestion des patients
Logique métier pour le suivi des patientes
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def patients_view(request):
    """
    Vue principale pour la gestion des patients
    """
    context = {
        'page_title': 'Patients',
        'section': 'patients'
    }
    return render(request, 'core/patients/index.html', context)


