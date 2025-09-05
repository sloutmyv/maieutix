from django import template
from datetime import date

register = template.Library()

@register.filter
def is_past_due(value):
    """
    Vérifie si une date est dépassée (dans le passé par rapport à aujourd'hui)
    """
    if not value:
        return False
    
    today = date.today()
    return value < today