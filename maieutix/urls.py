"""
URL configuration for maieutix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import (
    home_view, feuille_soins_view, outils_view, 
    statistiques_view
)
from core.views.consultation_preparation_naissance import (
    liste_consultations_preparation_naissance,
    save_consultation_preparation_naissance,
    consultation_preparation_naissance_detail,
    delete_consultation_preparation_naissance
)
from core.views.reeducation_perinee import (
    liste_reeducations_perinee,
    save_reeducation_perinee,
    reeducation_perinee_detail,
    delete_reeducation_perinee,
    patient_reeducations_perinee,
    reeducation_perinee_modal
)

urlpatterns = [
    path('', home_view, name='home'),
    path('feuille-soins/', feuille_soins_view, name='feuille_soins'),
    path('patients/', include('core.urls.patients', namespace='patients')),
    path('consultations-preparation-naissance/', liste_consultations_preparation_naissance, name='liste_consultations_preparation_naissance'),
    path('consultation-preparation-naissance/save/', save_consultation_preparation_naissance, name='save_consultation_preparation_naissance'),
    path('consultation-preparation-naissance/<int:consultation_id>/', consultation_preparation_naissance_detail, name='consultation_preparation_naissance_detail'),
    path('consultation-preparation-naissance/<int:consultation_id>/delete/', delete_consultation_preparation_naissance, name='delete_consultation_preparation_naissance'),
    # Rééducation du périnée URLs
    path('reeducations-perinee/', liste_reeducations_perinee, name='liste_reeducations_perinee'),
    path('reeducation-perinee/save/', save_reeducation_perinee, name='save_reeducation_perinee'),
    path('reeducation-perinee/<int:seance_id>/', reeducation_perinee_detail, name='reeducation_perinee_detail'),
    path('reeducation-perinee/<int:seance_id>/delete/', delete_reeducation_perinee, name='delete_reeducation_perinee'),
    path('patients/<int:patient_id>/reeducations-perinee/', patient_reeducations_perinee, name='patient_reeducations_perinee'),
    path('reeducation-perinee/modal/<int:patient_id>/', reeducation_perinee_modal, name='reeducation_perinee_modal'),
    path('outils/', outils_view, name='outils'),
    path('statistiques/', statistiques_view, name='statistiques'),
    path('administration/', include('core.urls.administration', namespace='administration')),
    path('auth/', include('authentication.urls', namespace='auth')),
    path('admin/', admin.site.urls),
]
