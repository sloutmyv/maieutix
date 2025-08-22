"""
URLs pour l'authentification des sages-femmes
"""
from django.urls import path
from authentication.views import (
    login_view,
    logout_view,
    change_password_view,
    change_password_required_view
)

app_name = 'auth'

urlpatterns = [
    path('connexion/', login_view, name='login'),
    path('deconnexion/', logout_view, name='logout'),
    path('changer-mot-de-passe/', change_password_view, name='change_password'),
    path('mot-de-passe-obligatoire/', change_password_required_view, name='change_password_required'),
]