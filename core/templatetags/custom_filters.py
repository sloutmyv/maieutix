"""
Filtres personnalisés pour les templates Django
"""

from django import template
import re

register = template.Library()

@register.filter
def replace_periods_with_breaks(value):
    """
    Remplace les points (avec ou sans espace après) par des sauts de ligne HTML
    """
    if not value:
        return value
    
    # Remplace ". " par ".<br>" et "." en fin de phrase par ".<br>"
    result = re.sub(r'\.(\s+|(?=[A-Z])|$)', '.<br>', str(value))
    return result