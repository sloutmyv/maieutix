"""
URLs pour les consultations obstétricales
"""

from django.urls import path
from core.views.consultation_obstetricale import (
    patient_consultations_obstetricales, consultation_obstetricale_modal, save_consultation_obstetricale,
    consultation_obstetricale_detail, consultation_obstetricale_quick_form, save_quick_consultation_obstetricale, 
    delete_consultation_obstetricale
)

app_name = 'consultations_obstetricales'

urlpatterns = [
    # Consultations obstétricales
    path('<int:patient_id>/consultations-obstetricales/', patient_consultations_obstetricales, name='patient_consultations_obstetricales'),
    path('<int:patient_id>/consultation-obstetricale/modal/', consultation_obstetricale_modal, name='consultation_obstetricale_modal'),
    path('<int:patient_id>/consultation-obstetricale/quick-form/', consultation_obstetricale_quick_form, name='consultation_obstetricale_quick_form'),
    path('<int:patient_id>/consultation-obstetricale/save-quick/', save_quick_consultation_obstetricale, name='save_quick_consultation_obstetricale'),
    path('consultation-obstetricale/save/', save_consultation_obstetricale, name='save_consultation_obstetricale'),
    path('consultation-obstetricale/<int:consultation_id>/', consultation_obstetricale_detail, name='consultation_obstetricale_detail'),
    path('consultation-obstetricale/<int:consultation_id>/delete/', delete_consultation_obstetricale, name='delete_consultation_obstetricale'),
]