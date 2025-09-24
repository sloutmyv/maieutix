from django.contrib import admin
from django.utils.html import format_html
from core.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['nom_complet_display', 'type_patient', 'age_display', 'mere_display', 'caisse', 'is_active', 'created_at']
    list_filter = ['type_patient', 'is_active', 'caisse', 'est_assure_titulaire', 'created_at']
    search_fields = ['nom', 'prenom', 'nom_jf', 'mere__nom', 'mere__prenom']
    readonly_fields = ['created_at', 'updated_at', 'age_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('type_patient', 'nom', 'prenom', 'date_naissance')
        }),
        ('Informations complémentaires', {
            'fields': ('nom_jf', 'profession', 'telephone', 'numero_ep'),
            'classes': ('collapse',)
        }),
        ('Spécifique femme', {
            'fields': ('date_debut_grossesse',),
            'classes': ('collapse',)
        }),
        ('Relation familiale', {
            'fields': ('mere',),
            'classes': ('collapse',)
        }),
        ('Assurance', {
            'fields': ('est_assure_titulaire', 'caisse'),
        }),
        ('Informations assuré principal', {
            'fields': ('nom_assure', 'prenom_assure', 'date_naissance_assure'),
            'classes': ('collapse',)
        }),
        ('Adresse assuré', {
            'fields': ('rue_assure', 'code_postal_assure', 'commune_assure'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mere', 'caisse')
    
    def nom_complet_display(self, obj):
        if obj.type_patient == 'bebe' and obj.mere:
            return format_html(
                '{} {} <span style="color: #666;">(bébé de {} {})</span>',
                obj.prenom, obj.nom, obj.mere.prenom, obj.mere.nom
            )
        return f"{obj.prenom} {obj.nom}"
    nom_complet_display.short_description = 'Patient'
    nom_complet_display.admin_order_field = 'nom'
    
    def age_display(self, obj):
        return obj.age_detail
    age_display.short_description = 'Âge'
    
    def mere_display(self, obj):
        if obj.mere:
            return f"{obj.mere.prenom} {obj.mere.nom}"
        return "-"
    mere_display.short_description = 'Mère'
    mere_display.admin_order_field = 'mere__nom'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Limiter les choix de mère aux femmes uniquement
        if 'mere' in form.base_fields:
            form.base_fields['mere'].queryset = Patient.objects.filter(type_patient='femme')
        
        return form
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        # Ajouter age_display seulement pour les objets existants (modification)
        if obj:
            fieldsets = list(fieldsets)
            # Modifier le premier fieldset pour inclure age_display
            first_fieldset = fieldsets[0]
            fields = list(first_fieldset[1]['fields'])
            if 'age_display' not in fields:
                fields.append('age_display')
            fieldsets[0] = (first_fieldset[0], {'fields': tuple(fields)})
        
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        # Validation supplémentaire côté admin
        obj.clean()
        super().save_model(request, obj, form, change)


class PatientInline(admin.TabularInline):
    model = Patient
    fk_name = 'mere'
    extra = 0
    fields = ['prenom', 'nom', 'date_naissance', 'telephone']
    readonly_fields = []
    verbose_name = "Bébé"
    verbose_name_plural = "Bébés"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(type_patient='bebe')


# Mise à jour de l'admin des patients femmes pour afficher leurs bébés
class PatientFemmeAdmin(PatientAdmin):
    inlines = [PatientInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(type_patient='femme')


# Enregistrement séparé pour une meilleure UX si nécessaire
# admin.site.register(Patient, PatientFemmeAdmin)