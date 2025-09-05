"""
URLs pour la gestion des patients
"""

from django.urls import path
from core.views.patients import (
    patients_view, patient_create, patient_edit, 
    patient_detail, patient_detail_modal, patient_toggle_active,
    search_meres, patient_details_for_baby, patient_antecedents, save_antecedents
)

app_name = 'patients'

urlpatterns = [
    path('', patients_view, name='patients_view'),
    path('create/', patient_create, name='patient_create'),
    path('<int:patient_id>/edit/', patient_edit, name='patient_edit'),
    path('<int:patient_id>/', patient_detail, name='patient_detail'),
    path('<int:patient_id>/modal/', patient_detail_modal, name='patient_detail_modal'),
    path('<int:patient_id>/toggle-active/', patient_toggle_active, name='patient_toggle_active'),
    path('<int:patient_id>/details-for-baby/', patient_details_for_baby, name='patient_details_for_baby'),
    path('<int:patient_id>/antecedents/', patient_antecedents, name='patient_antecedents'),
    path('save-antecedents/', save_antecedents, name='save_antecedents'),
    path('search-meres/', search_meres, name='search_meres'),
]