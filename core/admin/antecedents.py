"""
Configuration Admin pour les antécédents patients
"""

from django.contrib import admin
from core.models import Antecedents, FrottisCV


class FrottisCVInline(admin.TabularInline):
    """Inline pour les frottis cervico-vaginaux"""
    model = FrottisCV
    extra = 0
    fields = ('date_frottis', 'resultat')
    ordering = ('-date_frottis',)


@admin.register(Antecedents)
class AntecedentsAdmin(admin.ModelAdmin):
    """Configuration admin pour les antécédents"""
    
    list_display = ('patient', 'taille', 'poids', 'imc', 'medecin_traitant', 'updated_at')
    list_filter = ('asthme', 'diabete', 'hta', 'epilepsie', 'created_at')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin_traitant', 'gynecologue')
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient',)
        }),
        ('6.1.1 Biométrie', {
            'fields': ('taille', 'poids'),
            'classes': ('collapse',)
        }),
        ('Médecins', {
            'fields': ('medecin_traitant', 'gynecologue'),
            'classes': ('collapse',)
        }),
        ('ATCD Médicaux', {
            'fields': ('allergie', 'asthme', 'raa', 'diabete', 'hta', 'epilepsie', 'infection_urinaire'),
            'classes': ('collapse',)
        }),
        ('ATCD Obstétricaux', {
            'fields': ('atcd_obstetricaux',),
            'classes': ('collapse',)
        }),
        ('FCV', {
            'fields': ('fcv_notes',),
            'classes': ('collapse',)
        }),
        ('ATCD Familiaux', {
            'fields': ('atcd_fam_diabete', 'atcd_fam_hta', 'atcd_fam_cancer_sein', 'atcd_fam_hypercholesterolemie', 'atcd_fam_autre'),
            'classes': ('collapse',)
        }),
        ('ATCD Chirurgicaux et Contraception', {
            'fields': ('atcd_chirurgicaux', 'contraception'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [FrottisCVInline]
    
    def imc(self, obj):
        """Calcul de l'IMC"""
        if obj.taille and obj.poids:
            return round(obj.poids / (obj.taille ** 2), 2)
        return None
    imc.short_description = 'IMC'


@admin.register(FrottisCV)
class FrottisCVAdmin(admin.ModelAdmin):
    """Configuration admin pour les frottis cervico-vaginaux"""
    
    list_display = ('patient_nom', 'date_frottis', 'resultat_court', 'created_at')
    list_filter = ('date_frottis', 'created_at')
    search_fields = ('antecedents__patient__nom', 'antecedents__patient__prenom', 'resultat')
    date_hierarchy = 'date_frottis'
    ordering = ('-date_frottis',)
    
    fields = ('antecedents', 'date_frottis', 'resultat')
    
    
    def patient_nom(self, obj):
        """Nom complet de la patiente"""
        return obj.antecedents.patient.nom_complet
    patient_nom.short_description = 'Patiente'
    patient_nom.admin_order_field = 'antecedents__patient__nom'
    
    def resultat_court(self, obj):
        """Version courte du résultat"""
        return obj.resultat[:50] + "..." if len(obj.resultat) > 50 else obj.resultat
    resultat_court.short_description = 'Résultat'