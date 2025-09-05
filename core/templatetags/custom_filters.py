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


@register.filter
def replace_periods_with_breaks(value):
    """
    Replace periods with HTML line breaks for better formatting
    """
    if not value:
        return value
    return str(value).replace('.', '.<br>')