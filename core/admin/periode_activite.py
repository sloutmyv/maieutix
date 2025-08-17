"""
Configuration admin pour PeriodeActivite
Interface d'administration pour la gestion des périodes d'activité
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from core.models import PeriodeActivite


@admin.register(PeriodeActivite)
class PeriodeActiviteAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les périodes d'activité
    """
    
    list_display = [
        'sage_femme',
        'date_debut',
        'date_fin',
        'duree_affichage',
        'statut_colored',
        'commentaire_court'
    ]
    
    list_filter = [
        'sage_femme',
        'date_debut',
        'date_fin',
    ]
    
    search_fields = [
        'sage_femme__nom',
        'sage_femme__prenom',
        'commentaire'
    ]
    
    ordering = ['-date_debut']
    
    fieldsets = (
        ('Période d\'activité', {
            'fields': ('sage_femme', 'date_debut', 'date_fin')
        }),
        ('Informations complémentaires', {
            'fields': ('commentaire',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = []
    
    def get_readonly_fields(self, request, obj=None):
        """Rendre certains champs lecture seule selon le contexte"""
        readonly = list(self.readonly_fields)
        
        # Si on modifie une période existante, ne pas permettre de changer la sage-femme
        if obj:
            readonly.append('sage_femme')
        
        return readonly
    
    def duree_affichage(self, obj):
        """Affiche la durée de la période"""
        if obj.duree_jours == 0:
            return "Aujourd'hui"
        elif obj.duree_jours == 1:
            return "1 jour"
        else:
            return f"{obj.duree_jours} jours"
    duree_affichage.short_description = "Durée"
    
    def statut_colored(self, obj):
        """Affiche le statut avec couleur"""
        if obj.est_active:
            if obj.date_fin:
                # Active avec date de fin
                color = "green"
                icon = "✓"
            else:
                # Active sans date de fin (en cours)
                color = "blue"
                icon = "∞"
        else:
            if obj.date_debut > timezone.now().date():
                # À venir
                color = "orange"
                icon = "⏳"
            else:
                # Terminée
                color = "red"
                icon = "✗"
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.statut_display
        )
    statut_colored.short_description = "Statut"
    
    def commentaire_court(self, obj):
        """Affiche un commentaire tronqué"""
        if obj.commentaire:
            if len(obj.commentaire) > 50:
                return f"{obj.commentaire[:50]}..."
            return obj.commentaire
        return "-"
    commentaire_court.short_description = "Commentaire"
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('sage_femme')


class PeriodeActiviteInline(admin.TabularInline):
    """
    Inline pour afficher les périodes d'activité dans l'admin des SageFemme
    """
    model = PeriodeActivite
    extra = 1
    ordering = ['-date_debut']
    
    fields = ['date_debut', 'date_fin', 'statut_display_inline', 'commentaire']
    readonly_fields = ['statut_display_inline']
    
    def statut_display_inline(self, obj):
        """Affiche le statut dans l'inline"""
        if obj.pk:  # Si l'objet existe
            return obj.statut_display
        return "-"
    statut_display_inline.short_description = "Statut"
    
    def get_queryset(self, request):
        """Optimise les requêtes pour l'inline"""
        return super().get_queryset(request).order_by('-date_debut')