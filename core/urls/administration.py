"""
URLs pour l'administration
"""

from django.urls import path
from core.views.administration import (
    administration_sages_femmes_view,
    sagefemme_list_view,
    sagefemme_create_view,
    sagefemme_detail_view,
    sagefemme_update_view,
    sagefemme_delete_view,
    ajouter_periode_activite_view,
    modifier_periode_activite_view,
    supprimer_periode_activite_view,
    terminer_periode_activite_view,
    # Vues pour les actes médicaux
    administration_actes_view,
    acte_list_view,
    acte_create_view,
    acte_detail_view,
    acte_update_view,
    acte_delete_view,
    ajouter_tarif_periode_view,
    modifier_tarif_periode_view,
    supprimer_tarif_periode_view,
    # Vues pour les prestations
    administration_prestations_view,
    prestation_list_view,
    prestation_create_view,
    prestation_detail_view,
    prestation_update_view,
    prestation_delete_view,
    # Vues pour les caisses
    administration_caisses_view,
    caisse_list_view,
    caisse_create_view,
    caisse_detail_view,
    caisse_update_view,
    caisse_delete_view
)

app_name = 'administration'

urlpatterns = [
    # Vue principale des sages-femmes
    path('sages-femmes/', administration_sages_femmes_view, name='administration_sages_femmes'),
    
    # API HTMX pour les sages-femmes
    path('api/sages-femmes/', sagefemme_list_view, name='sagefemme_list'),
    path('api/sages-femmes/create/', sagefemme_create_view, name='sagefemme_create'),
    path('api/sages-femmes/<int:pk>/', sagefemme_detail_view, name='sagefemme_detail'),
    path('api/sages-femmes/<int:pk>/update/', sagefemme_update_view, name='sagefemme_update'),
    path('api/sages-femmes/<int:pk>/delete/', sagefemme_delete_view, name='sagefemme_delete'),
    # Les URLs d'activation/désactivation ont été supprimées - statut géré par les périodes
    
    # API pour les périodes d'activité
    path('api/sages-femmes/<int:pk>/periodes/', ajouter_periode_activite_view, name='ajouter_periode'),
    path('api/periodes/<int:pk>/modifier/', modifier_periode_activite_view, name='modifier_periode'),
    path('api/periodes/<int:pk>/supprimer/', supprimer_periode_activite_view, name='supprimer_periode'),
    path('api/periodes/<int:pk>/terminer/', terminer_periode_activite_view, name='terminer_periode'),
    
    # Vue principale des actes médicaux
    path('actes/', administration_actes_view, name='administration_actes'),
    
    # API HTMX pour les actes médicaux
    path('api/actes/', acte_list_view, name='acte_list'),
    path('api/actes/create/', acte_create_view, name='acte_create'),
    path('api/actes/<int:pk>/', acte_detail_view, name='acte_detail'),
    path('api/actes/<int:pk>/update/', acte_update_view, name='acte_update'),
    path('api/actes/<int:pk>/delete/', acte_delete_view, name='acte_delete'),
    
    # API pour les périodes tarifaires
    path('actes/<int:pk>/ajouter-tarif/', ajouter_tarif_periode_view, name='ajouter_tarif'),
    path('tarifs/<int:pk>/modifier/', modifier_tarif_periode_view, name='modifier_tarif'),
    path('tarifs/<int:pk>/supprimer/', supprimer_tarif_periode_view, name='supprimer_tarif'),
    
    # Vue principale des prestations
    path('prestations/', administration_prestations_view, name='administration_prestations'),
    
    # API HTMX pour les prestations
    path('api/prestations/', prestation_list_view, name='prestation_list'),
    path('api/prestations/create/', prestation_create_view, name='prestation_create'),
    path('api/prestations/<int:pk>/', prestation_detail_view, name='prestation_detail'),
    path('api/prestations/<int:pk>/update/', prestation_update_view, name='prestation_update'),
    path('api/prestations/<int:pk>/delete/', prestation_delete_view, name='prestation_delete'),
    
    # Vue principale des caisses
    path('caisses/', administration_caisses_view, name='administration_caisses'),
    
    # API HTMX pour les caisses
    path('api/caisses/', caisse_list_view, name='caisse_list'),
    path('api/caisses/create/', caisse_create_view, name='caisse_create'),
    path('api/caisses/<int:pk>/', caisse_detail_view, name='caisse_detail'),
    path('api/caisses/<int:pk>/update/', caisse_update_view, name='caisse_update'),
    path('api/caisses/<int:pk>/delete/', caisse_delete_view, name='caisse_delete'),
]