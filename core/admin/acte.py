from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from core.models import Acte, TarifPeriode


class TarifPeriodeInline(admin.TabularInline):
    """Inline pour les périodes tarifaires d'un acte"""
    model = TarifPeriode
    extra = 1
    fields = ('cout_xpf', 'date_debut', 'date_fin', 'statut_display')
    readonly_fields = ('statut_display',)
    ordering = ['-date_debut']
    
    def statut_display(self, obj):
        """Affiche le statut de la période avec couleur"""
        if obj.pk:
            statut = obj.statut
            colors = {
                'Actuel': 'green',
                'Futur': 'orange', 
                'Expiré': 'red'
            }
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                colors.get(statut, 'black'),
                statut
            )
        return '-'
    statut_display.short_description = "Statut"


@admin.register(Acte)
class ActeAdmin(admin.ModelAdmin):
    """Configuration admin pour les actes médicaux"""
    
    list_display = [
        'code',
        'libelle_court', 
        'tarif_actuel_display',
        'nb_periodes_tarifaires',
        'created_at'
    ]
    
    list_filter = [
        'created_at',
    ]
    
    search_fields = ['code', 'libelle']
    ordering = ['code']
    
    fieldsets = (
        ('Informations de l\'acte', {
            'fields': ('code', 'libelle')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TarifPeriodeInline]
    
    def libelle_court(self, obj):
        """Affiche le libellé tronqué"""
        return obj.libelle[:50] + '...' if len(obj.libelle) > 50 else obj.libelle
    libelle_court.short_description = "Libellé"
    
    def tarif_actuel_display(self, obj):
        """Affiche le tarif actuel"""
        tarif = obj.tarif_actuel
        if tarif:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} XPF</span>',
                tarif.cout_xpf
            )
        return format_html('<span style="color: red;">Aucun tarif</span>')
    tarif_actuel_display.short_description = "Tarif actuel"
    
    def nb_periodes_tarifaires(self, obj):
        """Affiche le nombre de périodes tarifaires"""
        count = obj.tarifs_periodes.count()
        return f"{count} période{'s' if count > 1 else ''}"
    nb_periodes_tarifaires.short_description = "Périodes tarifaires"


@admin.register(TarifPeriode)
class TarifPeriodeAdmin(admin.ModelAdmin):
    """Configuration admin pour les périodes tarifaires"""
    
    list_display = [
        'acte_code',
        'cout_xpf',
        'date_debut',
        'date_fin', 
        'statut_display',
        'created_at'
    ]
    
    list_filter = [
        'acte',
        'date_debut',
        'created_at'
    ]
    
    search_fields = ['acte__code', 'acte__libelle']
    ordering = ['-date_debut']
    
    fieldsets = (
        ('Acte et tarif', {
            'fields': ('acte', 'cout_xpf')
        }),
        ('Période de validité', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def acte_code(self, obj):
        """Affiche le code de l'acte"""
        return obj.acte.code
    acte_code.short_description = "Code acte"
    acte_code.admin_order_field = 'acte__code'
    
    def statut_display(self, obj):
        """Affiche le statut avec couleur"""
        statut = obj.statut
        colors = {
            'Actuel': 'green',
            'Futur': 'orange',
            'Expiré': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(statut, 'black'),
            statut
        )
    statut_display.short_description = "Statut"
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('acte')