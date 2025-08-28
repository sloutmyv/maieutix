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
    supprimer_tarif_periode_view
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
]