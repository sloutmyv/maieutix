from django.contrib import admin
from core.models.cadre_exercice import CadreExercice


@admin.register(CadreExercice)
class CadreExerciceAdmin(admin.ModelAdmin):
    """Configuration de l'administration pour CadreExercice"""
    
    list_display = ['label', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['label', 'description']
    ordering = ['label']
    
    fields = ['label', 'description']
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule"""
        if obj:  # Si on modifie un objet existant
            return ['created_at', 'updated_at']
        return []