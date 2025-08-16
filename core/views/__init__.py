"""
Views package pour Maieutix
Structure modulaire suivant l'architecture définie
"""

from .feuille_soins import feuille_soins_view, home_view
from .patients import patients_view
from .outils import outils_view
from .statistiques import statistiques_view
from .administration import administration_sages_femmes_view

__all__ = [
    'feuille_soins_view',
    'home_view', 
    'patients_view',
    'outils_view',
    'statistiques_view',
    'administration_sages_femmes_view',
]