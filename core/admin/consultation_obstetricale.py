"""
Administration des consultations obstétricales
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from core.models import ConsultationObstetricale


@admin.register(ConsultationObstetricale)
class ConsultationObstetricaleAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour les consultations obstétricales"""
    
    list_display = [
        'patient_link',
        'date_consultation_formatted',
        'sa_affichage',
        'motif_court',
        'tension_affichage',
        'poids_affichage',
        'created_at_formatted'
    ]
    
    list_filter = [
        'date_consultation',
        'created_at',
        'patient__caisse',
    ]
    
    search_fields = [
        'patient__nom',
        'patient__prenom',
        'motif',
        'examen',
        'prescription'
    ]
    
    ordering = ['-date_consultation', '-created_at']
    
    readonly_fields = [
        'semaines_amenorrhee',
        'tension_interpretation_display',
        'imc_display',
        'resume_consultation_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('patient', 'date_consultation', 'semaines_amenorrhee')
        }),
        ('Constantes vitales', {
            'fields': (
                ('tension_systolique', 'tension_diastolique'),
                'tension_interpretation_display',
                'poids',
                'imc_display'
            ),
            'classes': ('collapse',)
        }),
        ('Consultation', {
            'fields': ('motif', 'examen', 'prescription', 'notes')
        }),
        ('Résumé', {
            'fields': ('resume_consultation_display',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Filtres personnalisés pour la barre latérale
    list_per_page = 25
    date_hierarchy = 'date_consultation'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related(
            'patient',
            'patient__caisse'
        )
    
    # Méthodes d'affichage personnalisées
    def patient_link(self, obj):
        """Lien vers la patiente"""
        if obj.patient:
            url = reverse('admin:core_patient_change', args=[obj.patient.pk])
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url,
                obj.patient.nom_complet
            )
        return "-"
    patient_link.short_description = "Patiente"
    patient_link.admin_order_field = 'patient__nom'
    
    def date_consultation_formatted(self, obj):
        """Date de consultation formatée"""
        if obj.date_consultation:
            return obj.date_consultation.strftime('%d/%m/%Y')
        return "-"
    date_consultation_formatted.short_description = "Date"
    date_consultation_formatted.admin_order_field = 'date_consultation'
    
    def sa_affichage(self, obj):
        """Affichage de la SA (Semaines d'Aménorrhée)"""
        if obj.semaines_amenorrhee:
            return format_html(
                '<span style="background-color: #e8f5e8; padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
                obj.semaines_amenorrhee
            )
        return "-"
    sa_affichage.short_description = "SA"
    sa_affichage.admin_order_field = 'semaines_amenorrhee'
    
    def motif_court(self, obj):
        """Motif tronqué pour la liste"""
        if obj.motif:
            if len(obj.motif) > 50:
                return f"{obj.motif[:50]}..."
            return obj.motif
        return "-"
    motif_court.short_description = "Motif"
    motif_court.admin_order_field = 'motif'
    
    def tension_affichage(self, obj):
        """Affichage de la tension avec interprétation"""
        if obj.tension_complete:
            interpretation = obj.tension_interpretation
            if interpretation:
                if 'normale' in interpretation.lower():
                    color = 'green'
                elif 'hypertension' in interpretation.lower():
                    color = 'red'
                else:
                    color = 'orange'
                
                return format_html(
                    '<span style="color: {}">{}<br><small>{}</small></span>',
                    color,
                    obj.tension_complete,
                    interpretation
                )
            return obj.tension_complete
        return "-"
    tension_affichage.short_description = "Tension"
    tension_affichage.admin_order_field = 'tension_systolique'
    
    def poids_affichage(self, obj):
        """Affichage du poids avec IMC si disponible"""
        if obj.poids:
            result = f"{obj.poids} kg"
            if obj.imc:
                result += f"<br><small>IMC: {obj.imc}</small>"
            return format_html(result)
        return "-"
    poids_affichage.short_description = "Poids"
    poids_affichage.admin_order_field = 'poids'
    
    def created_at_formatted(self, obj):
        """Date de création formatée"""
        if obj.created_at:
            return obj.created_at.strftime('%d/%m/%Y %H:%M')
        return "-"
    created_at_formatted.short_description = "Créé le"
    created_at_formatted.admin_order_field = 'created_at'
    
    # Champs readonly personnalisés
    def tension_interpretation_display(self, obj):
        """Affichage de l'interprétation de la tension"""
        interpretation = obj.tension_interpretation
        if interpretation:
            if 'normale' in interpretation.lower():
                color = 'green'
            elif 'hypertension' in interpretation.lower():
                color = 'red'
            else:
                color = 'orange'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                interpretation
            )
        return "-"
    tension_interpretation_display.short_description = "Interprétation tension"
    
    def imc_display(self, obj):
        """Affichage de l'IMC avec interprétation"""
        if obj.imc:
            # Interprétation de l'IMC
            imc_value = obj.imc
            if imc_value < 18.5:
                interpretation = "Insuffisance pondérale"
                color = "blue"
            elif imc_value < 25:
                interpretation = "Poids normal"
                color = "green"
            elif imc_value < 30:
                interpretation = "Surpoids"
                color = "orange"
            else:
                interpretation = "Obésité"
                color = "red"
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} - {}</span>',
                color,
                imc_value,
                interpretation
            )
        return "-"
    imc_display.short_description = "IMC"
    
    def resume_consultation_display(self, obj):
        """Affichage du résumé de consultation"""
        if obj.resume_consultation:
            return format_html(
                '<div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{}</div>',
                obj.resume_consultation
            )
        return "-"
    resume_consultation_display.short_description = "Résumé"
    
    # Actions personnalisées
    actions = ['marquer_consultation_complete', 'exporter_consultations']
    
    def marquer_consultation_complete(self, request, queryset):
        """Action pour marquer les consultations comme complètes (exemple)"""
        # Cette action pourrait ajouter une note ou un flag
        count = 0
        for consultation in queryset:
            if not consultation.notes or 'CONSULTATION COMPLÈTE' not in consultation.notes:
                if consultation.notes:
                    consultation.notes += '\n\nCONSULTATION COMPLÈTE - ' + timezone.now().strftime('%d/%m/%Y %H:%M')
                else:
                    consultation.notes = 'CONSULTATION COMPLÈTE - ' + timezone.now().strftime('%d/%m/%Y %H:%M')
                consultation.save()
                count += 1
        
        self.message_user(request, f"{count} consultation(s) marquée(s) comme complète(s).")
    marquer_consultation_complete.short_description = "Marquer comme consultation complète"
    
    def exporter_consultations(self, request, queryset):
        """Action pour exporter les consultations sélectionnées"""
        # Placeholder pour une future fonctionnalité d'export
        self.message_user(request, f"{queryset.count()} consultation(s) sélectionnée(s) pour export.")
    exporter_consultations.short_description = "Exporter les consultations"
    
    # Personnalisation du formulaire
    class Media:
        css = {
            'all': ('admin/css/consultation_obstetricale.css',)
        }
        js = ('admin/js/consultation_obstetricale.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        """Personnaliser le formulaire selon le contexte"""
        form = super().get_form(request, obj, **kwargs)
        
        # Définir la date max à aujourd'hui pour le champ date_consultation
        if 'date_consultation' in form.base_fields:
            form.base_fields['date_consultation'].widget.attrs.update({
                'max': timezone.now().date()
            })
        
        return form