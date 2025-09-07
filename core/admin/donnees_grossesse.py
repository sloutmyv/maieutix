"""
Configuration Django Admin pour DonneesGrossesse
"""

from django.contrib import admin
from core.models import DonneesGrossesse


@admin.register(DonneesGrossesse)
class DonneesGrossesseAdmin(admin.ModelAdmin):
    """Configuration admin pour les données de grossesse"""
    
    list_display = [
        'patient', 
        'gestite_parite', 
        'gs_rh', 
        'lieu_accouchement',
        'has_data',
        'updated_at'
    ]
    
    list_filter = [
        'gs_rh',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'patient__nom',
        'patient__prenom', 
        'gestite_parite',
        'lieu_accouchement',
        'gs_rh'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('patient',)
        }),
        ('Obstétrique', {
            'fields': ('gestite_parite', 'facteurs_risque', 'lieu_accouchement'),
            'classes': ('collapse',)
        }),
        ('Analyses de base', {
            'fields': ('gs_rh', 'rai'),
            'classes': ('collapse',)
        }),
        ('Dépistages T1', {
            'fields': ('ht21', 'dpni'),
            'classes': ('collapse',)
        }),
        ('Sérologies', {
            'fields': ('toxo', 'rub', 'vih', 'tpha_vdrl'),
            'classes': ('collapse',)
        }),
        ('Hépatite B', {
            'fields': ('ag_hbs', 'ac_anti_hbs'),
            'classes': ('collapse',)
        }),
        ('Métabolisme', {
            'fields': ('glyc_jeun', 'hgpo'),
            'classes': ('collapse',)
        }),
        ('Numération', {
            'fields': ('hb', 'plaq'),
            'classes': ('collapse',)
        }),
        ('Analyses urinaires/vaginales', {
            'fields': ('pv', 'ecbu'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_data(self, obj):
        """Indicateur si des données sont saisies"""
        return obj.has_data
    has_data.short_description = 'Données saisies'
    has_data.boolean = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')