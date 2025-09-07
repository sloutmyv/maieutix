from datetime import timedelta
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def add_days(date, days):
    """
    Ajoute un nombre de jours à une date
    Usage: {{ date|add_days:30 }}
    """
    if date and days:
        try:
            return date + timedelta(days=int(days))
        except (ValueError, TypeError):
            return date
    return date

@register.simple_tag
def today():
    """
    Retourne la date d'aujourd'hui
    Usage: {% today %}
    """
    return timezone.now().date()

@register.filter
def duree_grossesse_restante(date_terme):
    """
    Calcule la durée restante jusqu'au terme de façon lisible
    Usage: {{ date_terme|duree_grossesse_restante }}
    """
    if not date_terme:
        return ""
    
    aujourd_hui = timezone.now().date()
    if date_terme <= aujourd_hui:
        return "Terme dépassé"
    
    delta = date_terme - aujourd_hui
    jours = delta.days
    
    if jours < 7:
        return f"{jours} jour{'s' if jours > 1 else ''}"
    elif jours < 30:
        semaines = jours // 7
        jours_reste = jours % 7
        if jours_reste == 0:
            return f"{semaines} semaine{'s' if semaines > 1 else ''}"
        else:
            return f"{semaines} semaine{'s' if semaines > 1 else ''} et {jours_reste} jour{'s' if jours_reste > 1 else ''}"
    else:
        mois = jours // 30
        jours_reste = jours % 30
        semaines_reste = jours_reste // 7
        
        if semaines_reste == 0:
            return f"{mois} mois"
        else:
            return f"{mois} mois et {semaines_reste} semaine{'s' if semaines_reste > 1 else ''}"