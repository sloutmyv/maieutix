"""
Views package pour Maieutix
Structure modulaire suivant l'architecture définie
"""

from .feuille_soins import feuille_soins_view, home_view
from .outils import outils_view
from .statistiques import statistiques_view
from .administration import administration_sages_femmes_view
from .consultation_gynecologique import (
    patient_consultations,
    consultation_modal,
    save_consultation,
    consultation_detail,
    consultation_quick_form,
    save_quick_consultation
)

__all__ = [
    'feuille_soins_view',
    'home_view',
    'outils_view',
    'statistiques_view',
    'administration_sages_femmes_view',
    'patient_consultations',
    'consultation_modal',
    'save_consultation',
    'consultation_detail',
    'consultation_quick_form',
    'save_quick_consultation',
]