from django.contrib import admin
from core.models.prestation import Prestation


@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    """Configuration de l'administration pour Prestation"""
    
    list_display = [
        'cadre_exercice', 
        'designation_short', 
        'cotation', 
        'acte_code',
        'tarif_display_admin',
        'created_at'
    ]
    list_filter = [
        'cadre_exercice', 
        'cotation',
        'created_at', 
        'updated_at'
    ]
    search_fields = [
        'designation', 
        'limite', 
        'entente_prealable',
        'observation',
        'cadre_exercice__label'
    ]
    ordering = ['cadre_exercice__label', 'designation']
    
    # Organisation des champs dans l'interface
    fieldsets = (
        ('Informations principales', {
            'fields': ('cadre_exercice', 'designation', 'limite', 'cotation')
        }),
        ('Acte associé', {
            'fields': ('acte',)
        }),
        ('Entente et assurances', {
            'fields': (
                'entente_prealable',
                'assurance_maladie',
                'assurance_maternite_normale',
                'assurance_maternite_pathologie'
            )
        }),
        ('Observations', {
            'fields': ('observation',),
            'classes': ('collapse',)
        }),
    )
    
    # Plus besoin de filter_horizontal car acte est maintenant une ForeignKey
    
    def designation_short(self, obj):
        """Affichage raccourci de la désignation"""
        return obj.designation[:60] + "..." if len(obj.designation) > 60 else obj.designation
    designation_short.short_description = 'Désignation'
    
    def acte_code(self, obj):
        """Affichage du code de l'acte"""
        try:
            return obj.acte_code
        except:
            return "Aucun"
    acte_code.short_description = 'Acte'
    
    def tarif_display_admin(self, obj):
        """Affichage du tarif calculé"""
        return obj.tarif_display
    tarif_display_admin.short_description = 'Tarif calculé'
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule"""
        if obj:  # Si on modifie un objet existant
            return ['created_at', 'updated_at']
        return []
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related(
            'cadre_exercice', 'acte'
        )