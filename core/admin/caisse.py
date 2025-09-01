from django.contrib import admin
from core.models import Caisse


@admin.register(Caisse)
class CaisseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'get_conditions_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nom']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom',)
        }),
        ('Conditions de paiement éligibles', {
            'fields': ('conditions_paiement_eligibles',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('conditions_paiement_eligibles',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('conditions_paiement_eligibles')
    
    def get_conditions_count(self, obj):
        return obj.conditions_paiement_eligibles.count()
    get_conditions_count.short_description = 'Nb conditions'