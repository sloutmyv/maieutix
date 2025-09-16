"""
Administration pour les rééducations du périnée
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import ReeducationPerinee


@admin.register(ReeducationPerinee)
class ReeducationPerineeAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les rééducations du périnée"""
    
    # Affichage de la liste
    list_display = [
        'patient_link',
        'date_consultation',
        'numero_seance_badge',
        'examen_clinique_resume',
        'created_by_link',
        'created_at_formatted'
    ]
    
    list_filter = [
        'date_consultation',
        ('patient__caisse', admin.RelatedFieldListFilter),
        ('created_by', admin.RelatedFieldListFilter),
        'numero_seance',
        'created_at',
    ]
    
    search_fields = [
        'patient__nom',
        'patient__prenom',
        'examen_clinique_travail',
        'a_prevoir',
        'created_by__nom',
        'created_by__prenom',
    ]
    
    # Organisation des champs
    fieldsets = (
        ('Informations générales', {
            'fields': ('patient', 'date_consultation', 'numero_seance'),
            'classes': ('wide',),
        }),
        ('Contenu de la séance', {
            'fields': ('examen_clinique_travail', 'a_prevoir'),
            'classes': ('wide',),
            'description': 'Détails de l\'examen clinique et du travail de rééducation effectué'
        }),
        ('Traçabilité', {
            'fields': ('created_by',),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    # Optimisation des requêtes
    list_select_related = ['patient', 'patient__caisse', 'created_by']
    
    # Filtres hiérarchiques
    date_hierarchy = 'date_consultation'
    
    # Actions personnalisées
    actions = ['marquer_seances_completes']
    
    def marquer_seances_completes(self, request, queryset):
        """Action pour marquer les séances comme complètes"""
        count = 0
        for seance in queryset:
            if not seance.examen_clinique_travail:
                seance.examen_clinique_travail = "Séance complétée"
                seance.save()
                count += 1
        
        if count:
            self.message_user(request, f"{count} séance(s) marquée(s) comme complétée(s).")
        else:
            self.message_user(request, "Aucune séance à marquer comme complétée.")
    
    marquer_seances_completes.short_description = "Marquer les séances sélectionnées comme complètes"
    
    # Méthodes d'affichage personnalisées
    def patient_link(self, obj):
        """Lien vers la patiente"""
        if obj.patient:
            url = reverse('admin:core_patient_change', args=[obj.patient.pk])
            return format_html(
                '<a href="{}" title="Voir le dossier de {}">{}</a>',
                url,
                obj.patient.nom_complet,
                obj.patient.nom_complet
            )
        return "-"
    patient_link.short_description = "Patiente"
    patient_link.admin_order_field = 'patient__nom'
    
    def numero_seance_badge(self, obj):
        """Affichage du numéro de séance avec badge bleu"""
        return format_html(
            '<span class="badge" style="background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Séance {}</span>',
            obj.numero_seance
        )
    numero_seance_badge.short_description = "Séance"
    numero_seance_badge.admin_order_field = 'numero_seance'
    
    def examen_clinique_resume(self, obj):
        """Résumé de l'examen clinique/travail"""
        if obj.examen_clinique_travail:
            resume = obj.examen_clinique_travail[:80]
            if len(obj.examen_clinique_travail) > 80:
                resume += "..."
            return format_html('<span title="{}">{}</span>', obj.examen_clinique_travail, resume)
        return format_html('<em style="color: #999;">Aucun examen renseigné</em>')
    examen_clinique_resume.short_description = "Examen clinique / Travail"
    
    def created_by_link(self, obj):
        """Lien vers la sage-femme créatrice"""
        if obj.created_by:
            url = reverse('admin:core_sagefemme_change', args=[obj.created_by.pk])
            return format_html(
                '<a href="{}" title="Voir le profil de {}">{} {}</a>',
                url,
                obj.created_by.nom_complet,
                obj.created_by.prenom,
                obj.created_by.nom
            )
        return format_html('<em style="color: #999;">Non renseignée</em>')
    created_by_link.short_description = "Sage-femme"
    created_by_link.admin_order_field = 'created_by__nom'
    
    def created_at_formatted(self, obj):
        """Date de création formatée"""
        return obj.created_at.strftime("%d/%m/%Y à %H:%M")
    created_at_formatted.short_description = "Créé le"
    created_at_formatted.admin_order_field = 'created_at'
    
    def get_queryset(self, request):
        """Optimisation des requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related('patient', 'patient__caisse', 'created_by')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personnalisation des champs de relation"""
        if db_field.name == "patient":
            # Filtrer pour ne montrer que les femmes actives
            kwargs["queryset"] = db_field.related_model.objects.filter(
                type_patient='femme', 
                is_active=True
            ).select_related('caisse').order_by('nom', 'prenom')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)