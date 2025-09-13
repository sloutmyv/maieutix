from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from core.models import EntretienPrenatalPrecoce, Patient


class EntretienPrenatalPrecoceForm(forms.ModelForm):
    """
    Formulaire principal pour les entretiens prénataux précoces
    """
    
    class Meta:
        model = EntretienPrenatalPrecoce
        fields = [
            'patient',
            'date_entretien',
            'conjoint_present',
            'lieu_accouchement_prevu',
            'atcd_marquants_sante',
            'environnement_social_familial',
            'projet_naissance_parentalite',
            'ressenti',
            'propositions_liens'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'required': True,
            }),
            'date_entretien': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'max': timezone.now().date(),
                'required': True,
            }),
            'conjoint_present': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'lieu_accouchement_prevu': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Maternité, clinique ou lieu prévu...',
                'maxlength': 200,
            }),
            'atcd_marquants_sante': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'ATCD marquants et santé globale...',
            }),
            'environnement_social_familial': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Contexte socio-familial, soutien, conditions de vie...',
            }),
            'projet_naissance_parentalite': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Projet de naissance et de parentalité...',
            }),
            'ressenti': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Ressenti de la patiente et du conjoint sur la grossesse...',
            }),
            'propositions_liens': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Propositions/liens...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limiter les patients aux femmes avec DDG
        self.fields['patient'].queryset = Patient.objects.filter(
            type_patient='femme',
            date_debut_grossesse__isnull=False
        ).order_by('nom', 'prenom')
        
        # Labels en français
        self.fields['patient'].label = "Patiente"
        self.fields['date_entretien'].label = "Date de l'entretien"
        self.fields['conjoint_present'].label = "Conjoint/partenaire présent"
        self.fields['lieu_accouchement_prevu'].label = "Lieu d'accouchement prévu"
        self.fields['atcd_marquants_sante'].label = "ATCD marquants et santé globale"
        self.fields['environnement_social_familial'].label = "Environnement social et familial"
        self.fields['projet_naissance_parentalite'].label = "Projet de naissance et de parentalité"
        self.fields['ressenti'].label = "Ressenti"
        self.fields['propositions_liens'].label = "Propositions/liens"
    
    def clean_date_entretien(self):
        """Validation de la date d'entretien"""
        date_entretien = self.cleaned_data.get('date_entretien')
        
        if date_entretien:
            if date_entretien > date.today():
                raise ValidationError("La date de l'entretien ne peut pas être dans le futur.")
        
        return date_entretien
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        date_entretien = cleaned_data.get('date_entretien')
        
        if patient and date_entretien:
            # Vérifier que la patiente a une DDG
            if not patient.date_debut_grossesse:
                raise ValidationError("La patiente sélectionnée doit avoir une date de début de grossesse définie.")
            
            # Vérifier que l'entretien a lieu après le début de grossesse
            if date_entretien < patient.date_debut_grossesse:
                raise ValidationError("La date de l'entretien doit être postérieure au début de grossesse.")
        
        return cleaned_data


class EntretienPrenatalPrecoceModalForm(EntretienPrenatalPrecoceForm):
    """
    Formulaire modal pour les entretiens prénataux précoces
    Utilisé dans les modales HTMX
    """
    
    def __init__(self, *args, patient_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si patient_id fourni, masquer le champ patient et le pré-remplir
        if patient_id:
            try:
                patient = Patient.objects.get(pk=patient_id)
                self.fields['patient'].initial = patient
                self.fields['patient'].widget = forms.HiddenInput()
            except Patient.DoesNotExist:
                pass
        
        # Ajuster les classes CSS pour modal
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                current_class = field.widget.attrs.get('class', '')
                if 'block w-full' in current_class:
                    field.widget.attrs['class'] = current_class.replace('sm:text-sm', 'text-sm')


class EntretienPrenatalPrecoceQuickForm(forms.ModelForm):
    """
    Formulaire rapide/inline pour créer un entretien prénatal précoce
    Version simplifiée avec les champs essentiels
    """
    
    class Meta:
        model = EntretienPrenatalPrecoce
        fields = [
            'date_entretien',
            'conjoint_present',
            'lieu_accouchement_prevu',
            'atcd_marquants_sante',
            'environnement_social_familial',
            'projet_naissance_parentalite',
            'ressenti',
            'propositions_liens'
        ]
        
        widgets = {
            'date_entretien': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'max': timezone.now().date(),
                'required': True,
            }),
            'conjoint_present': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 shadow-sm focus:border-green-500 focus:ring-green-500',
            }),
            'lieu_accouchement_prevu': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'placeholder': 'Lieu d\'accouchement prévu...',
                'maxlength': 200,
            }),
            'atcd_marquants_sante': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'rows': 4,
                'placeholder': 'ATCD marquants et santé globale...',
            }),
            'environnement_social_familial': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'rows': 4,
                'placeholder': 'Environnement social et familial...',
            }),
            'projet_naissance_parentalite': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'rows': 4,
                'placeholder': 'Projet de naissance et de parentalité...',
            }),
            'ressenti': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'rows': 4,
                'placeholder': 'Ressenti...',
            }),
            'propositions_liens': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm',
                'rows': 4,
                'placeholder': 'Propositions/liens...',
            }),
        }
    
    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Stocker la patiente
        self.patient = patient
        
        # Labels simplifiés
        self.fields['date_entretien'].label = "Date"
        self.fields['conjoint_present'].label = "Conjoint présent"
        self.fields['lieu_accouchement_prevu'].label = "Lieu accouchement"
        self.fields['atcd_marquants_sante'].label = "ATCD marquants et santé globale"
        self.fields['environnement_social_familial'].label = "Environnement social et familial"
        self.fields['projet_naissance_parentalite'].label = "Projet de naissance et de parentalité"
        self.fields['ressenti'].label = "Ressenti"
        self.fields['propositions_liens'].label = "Propositions/liens"
    
    def save(self, commit=True):
        """Sauvegarde avec assignation de la patiente"""
        entretien = super().save(commit=False)
        
        if self.patient:
            entretien.patient = self.patient
        
        if commit:
            entretien.save()
        
        return entretien
    
    def clean_date_entretien(self):
        """Validation de la date d'entretien"""
        date_entretien = self.cleaned_data.get('date_entretien')
        
        if date_entretien:
            if date_entretien > date.today():
                raise ValidationError("La date ne peut pas être dans le futur.")
            
            # Vérifier avec la patiente si disponible
            if self.patient and self.patient.date_debut_grossesse:
                if date_entretien < self.patient.date_debut_grossesse:
                    raise ValidationError("La date doit être postérieure au début de grossesse.")
        
        return date_entretien


class EntretienPrenatalPrecoceSearchForm(forms.Form):
    """
    Formulaire de recherche pour les entretiens prénataux précoces
    """
    
    recherche = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Rechercher par nom de patiente, lieu d\'accouchement...',
        }),
        label="Recherche"
    )
    
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
        label="Du"
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
        label="Au"
    )
    
    conjoint_present = forms.ChoiceField(
        choices=[
            ('', 'Tous'),
            ('oui', 'Conjoint présent'),
            ('non', 'Conjoint absent'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
        label="Présence conjoint"
    )
    
    sage_femme = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Toutes les sages-femmes",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
        }),
        label="Sage-femme"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Charger les sages-femmes actives
        from core.models import SageFemme
        self.fields['sage_femme'].queryset = SageFemme.objects.filter(
            is_active=True
        ).order_by('nom', 'prenom')