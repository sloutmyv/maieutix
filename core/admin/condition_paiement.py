from django.contrib import admin
from core.models import ConditionPaiement


@admin.register(ConditionPaiement)
class ConditionPaiementAdmin(admin.ModelAdmin):
    list_display = ['designation', 'pourcentage', 'created_at']
    list_filter = ['created_at']
    search_fields = ['designation']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('designation', 'pourcentage')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )