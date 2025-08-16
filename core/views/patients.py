"""
Views pour la gestion des patients
Logique métier pour le suivi des patientes
"""

from django.shortcuts import render


def patients_view(request):
    """
    Vue principale pour la gestion des patients
    """
    context = {
        'page_title': 'Patients',
        'section': 'patients'
    }
    return render(request, 'core/patients/index.html', context)


def patient_detail_view(request, patient_id):
    """
    Vue pour le détail d'un patient
    """
    context = {
        'page_title': 'Détail Patient',
        'patient_id': patient_id
    }
    return render(request, 'core/patients/detail.html', context)


def nouveau_patient_view(request):
    """
    Vue pour créer un nouveau patient
    """
    context = {
        'page_title': 'Nouveau Patient'
    }
    return render(request, 'core/patients/nouveau.html', context)