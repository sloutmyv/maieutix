"""
Formulaires pour les consultations de préparation à la naissance
"""

from django import forms
from django.forms.widgets import DateInput, Textarea, Select
from datetime import date

from core.models import ConsultationPreparationNaissance, Patient


class ConsultationPreparationNaissanceForm(forms.ModelForm):
    """
    Formulaire standard pour les consultations de préparation à la naissance
    """
    
    class Meta:
        model = ConsultationPreparationNaissance
        fields = [
            'patient',
            'date_consultation', 
            'theme_aborde',
            'a_prevoir'
        ]
        
        labels = {
            'patient': 'Patiente',
            'date_consultation': 'Date de consultation',
            'theme_aborde': 'Thème(s) abordé(s)',
            'a_prevoir': 'À prévoir',
        }
        
        help_texts = {
            'date_consultation': 'Date de la consultation (par défaut aujourd\'hui)',
            'theme_aborde': 'Thème principal abordé lors de cette consultation',
            'a_prevoir': 'Points à prévoir pour la prochaine consultation ou l\'accouchement',
        }
        
        widgets = {
            'patient': Select(attrs={
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'date_consultation': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'max': date.today().isoformat()
            }),
            'theme_aborde': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'Ex: Respiration et relaxation, Positions d\'accouchement, Allaitement maternel...'
            }),
            'a_prevoir': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'Ex: Revoir les exercices de respiration, Prévoir visite maternité...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrer les patients pour ne montrer que les femmes
        self.fields['patient'].queryset = Patient.objects.filter(
            type_patient='femme',
            is_active=True
        ).select_related('caisse').order_by('nom', 'prenom')
        
        # Date par défaut
        if not self.instance.pk:
            self.fields['date_consultation'].initial = date.today()
    
    def clean_date_consultation(self):
        """Validation de la date de consultation"""
        date_consultation = self.cleaned_data['date_consultation']
        
        if date_consultation and date_consultation > date.today():
            raise forms.ValidationError(
                "La date de consultation ne peut pas être dans le futur."
            )
        
        return date_consultation
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
        return instance


class ConsultationPreparationNaissanceModalForm(ConsultationPreparationNaissanceForm):
    """
    Formulaire modal HTMX pour les consultations de préparation à la naissance
    Optimisé pour une utilisation dans un modal avec patient pré-sélectionné
    """
    
    def __init__(self, *args, patient_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Masquer le champ patient dans le modal (sera passé par l'URL)
        if patient_id:
            self.fields['patient'].widget = forms.HiddenInput()
            try:
                patient = Patient.objects.get(pk=patient_id, type_patient='femme')
                self.fields['patient'].initial = patient
            except Patient.DoesNotExist:
                pass
        
        # Ajuster les classes CSS pour le modal
        for field_name, field in self.fields.items():
            if field_name != 'patient':
                if hasattr(field.widget, 'attrs'):
                    current_class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = current_class.replace('focus:ring-green-500', 'focus:ring-green-500')


class ConsultationPreparationNaissanceQuickForm(forms.ModelForm):
    """
    Formulaire rapide inline pour les consultations de préparation à la naissance
    Version simplifiée pour saisie rapide
    """
    
    class Meta:
        model = ConsultationPreparationNaissance
        fields = [
            'date_consultation',
            'theme_aborde',
            'a_prevoir'
        ]
        
        labels = {
            'date_consultation': 'Date',
            'theme_aborde': 'Thème(s) abordé(s)',
            'a_prevoir': 'À prévoir',
        }
        
        widgets = {
            'date_consultation': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-400',
                'max': date.today().isoformat()
            }),
            'theme_aborde': Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-400',
                'placeholder': 'Thème principal de cette consultation...'
            }),
            'a_prevoir': Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-400',
                'placeholder': 'Points à prévoir...'
            }),
        }
    
    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.patient = patient
        
        # Date par défaut aujourd'hui
        if not self.instance.pk:
            self.fields['date_consultation'].initial = date.today()
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        
        # Vérifier que le patient est bien une femme
        if self.patient and self.patient.type_patient != 'femme':
            raise forms.ValidationError(
                "Les consultations de préparation à la naissance sont réservées aux femmes."
            )
        
        return cleaned_data
    
    def clean_date_consultation(self):
        """Validation de la date de consultation"""
        date_consultation = self.cleaned_data['date_consultation']
        
        if date_consultation and date_consultation > date.today():
            raise forms.ValidationError(
                "La date de consultation ne peut pas être dans le futur."
            )
        
        return date_consultation
    
    def save(self, commit=True):
        """Sauvegarde avec assignation du patient"""
        instance = super().save(commit=False)
        
        # Assigner le patient
        if self.patient:
            instance.patient = self.patient
        
        if commit:
            instance.save()
        
        return instance


class ConsultationPreparationNaissanceSearchForm(forms.Form):
    """
    Formulaire de recherche pour les consultations de préparation à la naissance
    """
    
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500',
            'placeholder': 'Rechercher par nom, thème...'
        }),
        label='Recherche'
    )
    
    date_debut = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
        }),
        label='Date de début'
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
        }),
        label='Date de fin'
    )