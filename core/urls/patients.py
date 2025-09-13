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
from core.views.entretien_prenatal_precoce import (
    patient_entretiens_prenataux_precoces, entretien_prenatal_precoce_modal, save_entretien_prenatal_precoce,
    entretien_prenatal_precoce_detail, entretien_prenatal_precoce_quick_form, save_quick_entretien_prenatal_precoce,
    delete_entretien_prenatal_precoce
)
from core.views.consultation_preparation_naissance import (
    patient_consultations_preparation_naissance, consultation_preparation_naissance_modal, save_consultation_preparation_naissance,
    consultation_preparation_naissance_detail, consultation_preparation_naissance_quick_form, save_quick_consultation_preparation_naissance,
    delete_consultation_preparation_naissance
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
    
    # Entretiens prénataux précoces
    path('<int:patient_id>/entretiens-prenataux-precoces/', patient_entretiens_prenataux_precoces, name='patient_entretiens_prenataux_precoces'),
    path('<int:patient_id>/entretien-prenatal-precoce/modal/', entretien_prenatal_precoce_modal, name='entretien_prenatal_precoce_modal'),
    path('<int:patient_id>/entretien-prenatal-precoce/quick-form/', entretien_prenatal_precoce_quick_form, name='entretien_prenatal_precoce_quick_form'),
    path('<int:patient_id>/entretien-prenatal-precoce/save-quick/', save_quick_entretien_prenatal_precoce, name='save_quick_entretien_prenatal_precoce'),
    path('entretien-prenatal-precoce/save/', save_entretien_prenatal_precoce, name='save_entretien_prenatal_precoce'),
    path('entretien-prenatal-precoce/<int:entretien_id>/', entretien_prenatal_precoce_detail, name='entretien_prenatal_precoce_detail'),
    path('entretien-prenatal-precoce/<int:entretien_id>/delete/', delete_entretien_prenatal_precoce, name='delete_entretien_prenatal_precoce'),
    
    # Consultations préparation naissance
    path('<int:patient_id>/consultations-preparation-naissance/', patient_consultations_preparation_naissance, name='patient_consultations_preparation_naissance'),
    path('<int:patient_id>/consultation-preparation-naissance/modal/', consultation_preparation_naissance_modal, name='consultation_preparation_naissance_modal'),
    path('<int:patient_id>/consultation-preparation-naissance/quick-form/', consultation_preparation_naissance_quick_form, name='consultation_preparation_naissance_quick_form'),
    path('<int:patient_id>/consultation-preparation-naissance/save-quick/', save_quick_consultation_preparation_naissance, name='save_quick_consultation_preparation_naissance'),
    path('consultation-preparation-naissance/save/', save_consultation_preparation_naissance, name='save_consultation_preparation_naissance'),
    path('consultation-preparation-naissance/<int:consultation_id>/', consultation_preparation_naissance_detail, name='consultation_preparation_naissance_detail'),
    path('consultation-preparation-naissance/<int:consultation_id>/delete/', delete_consultation_preparation_naissance, name='delete_consultation_preparation_naissance'),
    
    path('search-meres/', search_meres, name='search_meres'),
]