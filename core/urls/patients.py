"""
URLs pour la gestion des patients
"""

from django.urls import path
from core.views.patients import (
    patients_view, patient_create, patient_edit, 
    patient_detail, patient_detail_modal, patient_toggle_active,
    search_meres, patient_details_for_baby, patient_antecedents, save_antecedents, update_ddg, reload_pregnancy_calendar,
    patient_donnees_grossesse, save_donnees_grossesse
)
from core.views.consultation_gynecologique import (
    patient_consultations, consultation_modal, save_consultation,
    consultation_detail, consultation_quick_form, save_quick_consultation, delete_consultation
)
from core.views.consultation_obstetricale import (
    patient_consultations_obstetricales, consultation_obstetricale_modal, save_consultation_obstetricale,
    consultation_obstetricale_detail, consultation_obstetricale_quick_form, save_quick_consultation_obstetricale, 
    delete_consultation_obstetricale
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
    
    # Antécédents
    path('<int:patient_id>/antecedents/', patient_antecedents, name='patient_antecedents'),
    path('save-antecedents/', save_antecedents, name='save_antecedents'),
    
    # Date de début de grossesse
    path('<int:patient_id>/update-ddg/', update_ddg, name='update_ddg'),
    path('<int:patient_id>/reload-pregnancy-calendar/', reload_pregnancy_calendar, name='reload_pregnancy_calendar'),
    
    # Données de grossesse
    path('<int:patient_id>/donnees-grossesse/', patient_donnees_grossesse, name='patient_donnees_grossesse'),
    path('save-donnees-grossesse/', save_donnees_grossesse, name='save_donnees_grossesse'),
    
    # Consultations gynécologiques
    path('<int:patient_id>/consultations/', patient_consultations, name='patient_consultations'),
    path('<int:patient_id>/consultation/modal/', consultation_modal, name='consultation_modal'),
    path('<int:patient_id>/consultation/quick-form/', consultation_quick_form, name='consultation_quick_form'),
    path('<int:patient_id>/consultation/save-quick/', save_quick_consultation, name='save_quick_consultation'),
    path('consultation/save/', save_consultation, name='save_consultation'),
    path('consultation/<int:consultation_id>/', consultation_detail, name='consultation_detail'),
    path('consultation/<int:consultation_id>/delete/', delete_consultation, name='delete_consultation'),
    
    # Consultations obstétricales
    path('<int:patient_id>/consultations-obstetricales/', patient_consultations_obstetricales, name='patient_consultations_obstetricales'),
    path('<int:patient_id>/consultation-obstetricale/modal/', consultation_obstetricale_modal, name='consultation_obstetricale_modal'),
    path('<int:patient_id>/consultation-obstetricale/quick-form/', consultation_obstetricale_quick_form, name='consultation_obstetricale_quick_form'),
    path('<int:patient_id>/consultation-obstetricale/save-quick/', save_quick_consultation_obstetricale, name='save_quick_consultation_obstetricale'),
    path('consultation-obstetricale/save/', save_consultation_obstetricale, name='save_consultation_obstetricale'),
    path('consultation-obstetricale/<int:consultation_id>/', consultation_obstetricale_detail, name='consultation_obstetricale_detail'),
    path('consultation-obstetricale/<int:consultation_id>/delete/', delete_consultation_obstetricale, name='delete_consultation_obstetricale'),
    
    path('search-meres/', search_meres, name='search_meres'),
]