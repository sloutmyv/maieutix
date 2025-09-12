from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from core.models import EntretienPrenatalPrecoce


@admin.register(EntretienPrenatalPrecoce)
class EntretienPrenatalPrecoceAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les entretiens prénataux précoces
    """
    
    list_display = [
        'patient_link',
        'date_entretien_formatted', 
        'sa_affichage',
        'conjoint_present_display',
        'lieu_accouchement_court',
        'periode_indicator',
        'sage_femme_display',
        'created_at_formatted'
    ]
    
    list_filter = [
        'date_entretien',
        'conjoint_present',
        'created_at',
        'patient__caisse',
        'sage_femme',
    ]
    
    search_fields = [
        'patient__nom',
        'patient__prenom', 
        'lieu_accouchement_prevu',
        'atcd_marquants',
        'projet_naissance',
        'notes'
    ]
    
    readonly_fields = [
        'semaines_amenorrhee',
        'entretien_resume_display',
        'periode_indicator_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'patient',
                'sage_femme',
                'date_entretien',
                'semaines_amenorrhee'
            )
        }),
        ('Contexte de l\'entretien', {
            'fields': (
                'conjoint_present',
                'lieu_accouchement_prevu',
            )
        }),
        ('Contenu de l\'entretien', {
            'fields': (
                'atcd_marquants',
                'environnement_social_familial',
                'projet_naissance',
                'projet_parental',
                'ressenti',
                'propositions_liens',
            )
        }),
        ('Notes et résumé', {
            'fields': (
                'notes',
                'entretien_resume_display',
                'periode_indicator_display',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-date_entretien', '-created_at']
    date_hierarchy = 'date_entretien'
    list_per_page = 25
    
    # Optimisation des requêtes
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'patient', 
            'patient__caisse',
            'sage_femme',
            'created_by'
        )
    
    # Méthodes d'affichage personnalisées
    def patient_link(self, obj):
        """Lien vers la fiche patiente"""
        if obj.patient:
            url = reverse('admin:core_patient_change', args=[obj.patient.pk])
            return format_html(
                '<a href="{}" target="_blank" title="Voir la fiche patiente">{}</a>',
                url, obj.patient.nom_complet
            )
        return "-"
    patient_link.short_description = "Patiente"
    patient_link.admin_order_field = 'patient__nom'
    
    def date_entretien_formatted(self, obj):
        """Date d'entretien formatée"""
        if obj.date_entretien:
            return obj.date_entretien.strftime('%d/%m/%Y')
        return "-"
    date_entretien_formatted.short_description = "Date entretien"
    date_entretien_formatted.admin_order_field = 'date_entretien'
    
    def sa_affichage(self, obj):
        """Affichage SA avec badge coloré"""
        if obj.semaines_amenorrhee:
            # Badge vert pour les SA
            return format_html(
                '<span style="background-color: #e8f5e8; color: #2d5a2d; padding: 2px 8px; '
                'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
                obj.semaines_amenorrhee
            )
        return "-"
    sa_affichage.short_description = "SA"
    
    def conjoint_present_display(self, obj):
        """Affichage présence conjoint avec icône"""
        if obj.conjoint_present:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;" title="Conjoint présent">👥 Oui</span>'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;" title="Conjoint absent">👤 Non</span>'
            )
    conjoint_present_display.short_description = "Conjoint"
    conjoint_present_display.admin_order_field = 'conjoint_present'
    
    def lieu_accouchement_court(self, obj):
        """Lieu d'accouchement raccourci"""
        if obj.lieu_accouchement_prevu:
            lieu = obj.lieu_accouchement_prevu[:30]
            if len(obj.lieu_accouchement_prevu) > 30:
                lieu += "..."
            return format_html(
                '<span title="{}">{}</span>',
                obj.lieu_accouchement_prevu, lieu
            )
        return "-"
    lieu_accouchement_court.short_description = "Lieu accouchement"
    
    def periode_indicator(self, obj):
        """Indicateur de période optimale"""
        indicator = obj.indicateur_periode
        
        if indicator == "optimal":
            return format_html(
                '<span style="background-color: #d4edda; color: #155724; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px; font-weight: bold;">OPTIMAL</span>'
            )
        elif indicator == "limite":
            return format_html(
                '<span style="background-color: #fff3cd; color: #856404; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px; font-weight: bold;">LIMITE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #f8f9fa; color: #6c757d; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px;">?</span>'
            )
    periode_indicator.short_description = "Période"
    
    def sage_femme_display(self, obj):
        """Affichage sage-femme"""
        if obj.sage_femme:
            return f"{obj.sage_femme.prenom} {obj.sage_femme.nom}"
        return "-"
    sage_femme_display.short_description = "Sage-femme"
    sage_femme_display.admin_order_field = 'sage_femme__nom'
    
    def created_at_formatted(self, obj):
        """Date de création formatée"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"
    created_at_formatted.admin_order_field = 'created_at'
    
    def entretien_resume_display(self, obj):
        """Résumé de l'entretien pour l'admin"""
        return format_html(
            '<div style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; '
            'border-left: 3px solid #007bff; font-size: 12px;">'
            '<strong>Résumé :</strong><br>{}</div>',
            obj.entretien_resume
        )
    entretien_resume_display.short_description = "Résumé entretien"
    
    def periode_indicator_display(self, obj):
        """Indicateur de période avec explication"""
        est_optimal = obj.est_dans_periode_optimale
        
        if est_optimal is True:
            color = "#d4edda"
            text_color = "#155724"
            status = "PÉRIODE OPTIMALE"
            detail = "Entretien réalisé entre 16 et 28 SA (période recommandée)"
        elif est_optimal is False:
            color = "#fff3cd" 
            text_color = "#856404"
            status = "HORS PÉRIODE OPTIMALE"
            detail = "Entretien réalisé en dehors de la période 16-28 SA"
        else:
            color = "#f8f9fa"
            text_color = "#6c757d"
            status = "PÉRIODE INDÉTERMINÉE"
            detail = "Impossible de déterminer si la période est optimale"
        
        return format_html(
            '<div style="background-color: {}; color: {}; padding: 8px; border-radius: 4px; '
            'font-size: 11px; font-weight: bold; text-align: center;">'
            '{}<br><small style="font-weight: normal; font-style: italic;">{}</small></div>',
            color, text_color, status, detail
        )
    periode_indicator_display.short_description = "Analyse période"
    
    # Actions personnalisées
    def marquer_entretien_complet(self, request, queryset):
        """Action pour marquer l'entretien comme complet"""
        count = 0
        for entretien in queryset:
            if not entretien.notes or "ENTRETIEN COMPLET" not in entretien.notes:
                entretien.notes = f"{entretien.notes}\n\n--- ENTRETIEN COMPLET ---\nMarqué le {timezone.now().strftime('%d/%m/%Y à %H:%M')}" 
                entretien.save()
                count += 1
        
        self.message_user(request, f"{count} entretien(s) marqué(s) comme complet(s).")
    marquer_entretien_complet.short_description = "Marquer comme entretien complet"
    
    def exporter_entretiens(self, request, queryset):
        """Action pour exporter les entretiens sélectionnés"""
        # Placeholder pour future implémentation d'export
        count = queryset.count()
        self.message_user(request, f"Export de {count} entretien(s) sélectionné(s) (fonctionnalité à implémenter).")
    exporter_entretiens.short_description = "Exporter les entretiens sélectionnés"
    
    actions = [marquer_entretien_complet, exporter_entretiens]
    
    # Configuration du formulaire
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Date max = aujourd'hui
        if 'date_entretien' in form.base_fields:
            form.base_fields['date_entretien'].widget.attrs['max'] = timezone.now().date()
        
        return form
    
    # CSS et JS personnalisés
    class Media:
        css = {
            'all': ('admin/css/entretien_prenatal_precoce.css',)
        }
        js = ('admin/js/entretien_prenatal_precoce.js',)