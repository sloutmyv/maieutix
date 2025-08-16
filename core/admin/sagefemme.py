from django.contrib import admin
from django.forms import ModelForm
from core.models.sagefemme import SageFemme


class SageFemmeAdminForm(ModelForm):
    """Formulaire personnalisé pour l'administration des sages-femmes"""
    
    class Meta:
        model = SageFemme
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnalisation du champ remplacement_de
        if 'remplacement_de' in self.fields:
            self.fields['remplacement_de'].queryset = SageFemme.objects.filter(
                situation__in=['gerant', 'collaborateur'],
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
    
    def clean(self):
        cleaned_data = super().clean()
        situation = cleaned_data.get('situation')
        remplacement_de = cleaned_data.get('remplacement_de')
        
        # Validation côté formulaire pour cohérence
        if situation == 'remplacant' and not remplacement_de:
            self.add_error('remplacement_de', 'Ce champ est obligatoire pour un remplaçant.')
        
        if situation in ['gerant', 'collaborateur'] and remplacement_de:
            self.add_error('remplacement_de', 'Ce champ doit être vide pour un gérant ou collaborateur.')
        
        return cleaned_data


@admin.register(SageFemme)
class SageFemmeAdmin(admin.ModelAdmin):
    form = SageFemmeAdminForm
    
    list_display = [
        'nom_complet_display',
        'titre',
        'situation',
        'telephone',
        'email',
        'is_active',
        'updated_at'
    ]
    
    list_filter = [
        'situation',
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'nom',
        'prenom', 
        'titre',
        'telephone',
        'email',
        'numero_cafat',
        'ridet'
    ]
    
    list_editable = ['is_active']
    
    ordering = ['nom', 'prenom']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'titre')
        }),
        ('Contact', {
            'fields': ('telephone', 'email')
        }),
        ('Adresse', {
            'fields': ('rue', 'code_postal', 'ville'),
            'classes': ('collapse',),
            'description': 'Adresse optionnelle'
        }),
        ('Informations professionnelles', {
            'fields': ('numero_cafat', 'ridet', 'rib', 'banque')
        }),
        ('Situation professionnelle', {
            'fields': ('situation', 'remplacement_de')
        }),
        ('Options pour remplaçants', {
            'fields': ('etat_recapitulatif_commun', 'bons_depot_communs'),
            'classes': ('collapse',),
            'description': 'Options disponibles uniquement pour les remplaçants'
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def nom_complet_display(self, obj):
        """Affichage du nom complet dans la liste"""
        return obj.nom_complet
    nom_complet_display.short_description = "Nom complet"
    nom_complet_display.admin_order_field = 'nom'
    
    def get_form(self, request, obj=None, **kwargs):
        """Personnalisation du formulaire selon le contexte"""
        form = super().get_form(request, obj, **kwargs)
        
        # Ajout de classes CSS pour la gestion dynamique des champs
        if hasattr(form.base_fields, 'situation'):
            form.base_fields['situation'].widget.attrs.update({
                'onchange': 'toggleRemplacantFields(this.value)'
            })
        
        return form
    
    def get_readonly_fields(self, request, obj=None):
        """Champs en lecture seule selon le contexte"""
        readonly = list(self.readonly_fields)
        
        # Ajouter les métadonnées pour les objets existants
        if obj:
            readonly.extend(['created_at', 'updated_at'])
        
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Personnalisation de la sauvegarde"""
        # Log de l'action
        if change:
            # Modification
            pass
        else:
            # Création
            pass
        
        super().save_model(request, obj, form, change)
    
    class Media:
        js = ('admin/js/sagefemme_admin.js',)
        css = {
            'all': ('admin/css/sagefemme_admin.css',)
        }