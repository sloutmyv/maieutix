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
from django.urls import path
from core.views import (
    home_view, feuille_soins_view, patients_view, outils_view, 
    statistiques_view, administration_sages_femmes_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('feuille-soins/', feuille_soins_view, name='feuille_soins'),
    path('patients/', patients_view, name='patients'),
    path('outils/', outils_view, name='outils'),
    path('statistiques/', statistiques_view, name='statistiques'),
    path('administration/sages-femmes/', administration_sages_femmes_view, name='administration_sages_femmes'),
    path('admin/', admin.site.urls),
]
