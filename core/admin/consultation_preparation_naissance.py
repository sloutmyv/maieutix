from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from core.models import ConsultationPreparationNaissance


@admin.register(ConsultationPreparationNaissance)
class ConsultationPreparationNaissanceAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les consultations de préparation à la naissance
    """
    
    list_display = [
        'patient_link',
        'date_consultation_formatted', 
        'sa_affichage',
        'theme_aborde_court',
        'a_prevoir_court',
        'created_by_display',
        'created_at_formatted'
    ]
    
    list_filter = [
        'date_consultation',
        'created_at',
        'patient__caisse',
        'created_by',
    ]
    
    search_fields = [
        'patient__nom',
        'patient__prenom', 
        'theme_aborde',
        'a_prevoir',
    ]
    
    readonly_fields = [
        'semaines_amenorrhee',
        'consultation_resume_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'patient',
                'created_by',
                'date_consultation',
                'semaines_amenorrhee'
            )
        }),
        ('Contenu de la consultation', {
            'fields': (
                'theme_aborde',
                'a_prevoir',
            )
        }),
        ('Résumé', {
            'fields': (
                'consultation_resume_display',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-date_consultation', '-created_at']
    date_hierarchy = 'date_consultation'
    list_per_page = 25
    
    # Optimisation des requêtes
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'patient', 
            'patient__caisse',
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
    
    def date_consultation_formatted(self, obj):
        """Date de consultation formatée"""
        if obj.date_consultation:
            return obj.date_consultation.strftime('%d/%m/%Y')
        return "-"
    date_consultation_formatted.short_description = "Date consultation"
    date_consultation_formatted.admin_order_field = 'date_consultation'
    
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
    
    def theme_aborde_court(self, obj):
        """Thème abordé raccourci"""
        if obj.theme_aborde:
            theme = obj.theme_aborde[:40]
            if len(obj.theme_aborde) > 40:
                theme += "..."
            return format_html(
                '<span title="{}">{}</span>',
                obj.theme_aborde, theme
            )
        return "-"
    theme_aborde_court.short_description = "Thème(s) abordé(s)"
    
    def a_prevoir_court(self, obj):
        """À prévoir raccourci"""
        if obj.a_prevoir:
            prevoir = obj.a_prevoir[:40]
            if len(obj.a_prevoir) > 40:
                prevoir += "..."
            return format_html(
                '<span title="{}">{}</span>',
                obj.a_prevoir, prevoir
            )
        return "-"
    a_prevoir_court.short_description = "À prévoir"
    
    def created_by_display(self, obj):
        """Affichage sage-femme créatrice"""
        if obj.created_by:
            return f"{obj.created_by.prenom} {obj.created_by.nom}"
        return "-"
    created_by_display.short_description = "Sage-femme"
    created_by_display.admin_order_field = 'created_by__nom'
    
    def created_at_formatted(self, obj):
        """Date de création formatée"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"
    created_at_formatted.admin_order_field = 'created_at'
    
    def consultation_resume_display(self, obj):
        """Résumé de la consultation pour l'admin"""
        return format_html(
            '<div style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; '
            'border-left: 3px solid #22c55e; font-size: 12px;">'
            '<strong>Résumé :</strong><br>{}</div>',
            obj.consultation_resume
        )
    consultation_resume_display.short_description = "Résumé consultation"
    
    # Actions personnalisées
    def marquer_consultation_complete(self, request, queryset):
        """Action pour marquer la consultation comme complète"""
        count = 0
        for consultation in queryset:
            if not consultation.a_prevoir or "CONSULTATION COMPLÈTE" not in consultation.a_prevoir:
                from django.utils import timezone
                consultation.a_prevoir = f"{consultation.a_prevoir}\n\n--- CONSULTATION COMPLÈTE ---\nMarqué le {timezone.now().strftime('%d/%m/%Y à %H:%M')}" 
                consultation.save()
                count += 1
        
        self.message_user(request, f"{count} consultation(s) marquée(s) comme complète(s).")
    marquer_consultation_complete.short_description = "Marquer comme consultation complète"
    
    def exporter_consultations(self, request, queryset):
        """Action pour exporter les consultations sélectionnées"""
        # Placeholder pour future implémentation d'export
        count = queryset.count()
        self.message_user(request, f"Export de {count} consultation(s) sélectionnée(s) (fonctionnalité à implémenter).")
    exporter_consultations.short_description = "Exporter les consultations sélectionnées"
    
    actions = [marquer_consultation_complete, exporter_consultations]
    
    # Configuration du formulaire
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Date max = aujourd'hui
        if 'date_consultation' in form.base_fields:
            from django.utils import timezone
            form.base_fields['date_consultation'].widget.attrs['max'] = timezone.now().date()
        
        return form
    
    # CSS et JS personnalisés
    class Media:
        css = {
            'all': ('admin/css/consultation_preparation_naissance.css',)
        }
        js = ('admin/js/consultation_preparation_naissance.js',)