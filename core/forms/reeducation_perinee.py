"""
Formulaires pour les rééducations du périnée
"""

from django import forms
from django.forms.widgets import DateInput, Textarea, NumberInput
from datetime import date

from core.models import ReeducationPerinee, Patient


class ReeducationPerineeForm(forms.ModelForm):
    """
    Formulaire standard pour les rééducations du périnée
    """
    
    class Meta:
        model = ReeducationPerinee
        fields = [
            'patient',
            'date_consultation',
            'numero_seance',
            'examen_clinique_travail',
            'a_prevoir'
        ]
        
        labels = {
            'patient': 'Patiente',
            'date_consultation': 'Date de la séance',
            'numero_seance': 'Numéro de séance',
            'examen_clinique_travail': 'Examen clinique / Travail de rééducation',
            'a_prevoir': 'À prévoir',
        }
        
        help_texts = {
            'date_consultation': 'Date de la séance (par défaut aujourd\'hui)',
            'numero_seance': 'Numéro de la séance (commence à 1)',
            'examen_clinique_travail': 'Examen clinique effectué et travail de rééducation réalisé lors de la séance',
            'a_prevoir': 'Points à prévoir pour la prochaine séance ou recommandations',
        }
        
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'date_consultation': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'max': date.today().isoformat()
            }),
            'numero_seance': NumberInput(attrs={
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': 1,
                'step': 1
            }),
            'examen_clinique_travail': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Évaluation du tonus périnéal, exercices de contractions...'
            }),
            'a_prevoir': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Continuer les exercices à domicile, revoir technique...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrer les patients pour ne montrer que les femmes actives
        self.fields['patient'].queryset = Patient.objects.filter(
            type_patient='femme',
            is_active=True
        ).select_related('caisse').order_by('nom', 'prenom')
        
        # Date par défaut
        if not self.instance.pk:
            self.fields['date_consultation'].initial = date.today()
            # Calculer le prochain numéro de séance automatiquement
            if 'patient' in self.data or (hasattr(self, 'initial') and 'patient' in self.initial):
                patient_id = self.data.get('patient') or self.initial.get('patient')
                if patient_id:
                    try:
                        patient = Patient.objects.get(pk=patient_id)
                        last_seance = patient.reeducations_perinee.order_by('-numero_seance').first()
                        if last_seance:
                            self.fields['numero_seance'].initial = last_seance.numero_seance + 1
                    except Patient.DoesNotExist:
                        pass
    
    def clean_date_consultation(self):
        """Validation de la date de consultation"""
        date_consultation = self.cleaned_data['date_consultation']
        
        if date_consultation and date_consultation > date.today():
            raise forms.ValidationError(
                "La date de la séance ne peut pas être dans le futur."
            )
        
        return date_consultation
    
    def clean_numero_seance(self):
        """Validation du numéro de séance"""
        numero_seance = self.cleaned_data['numero_seance']
        
        if numero_seance and numero_seance < 1:
            raise forms.ValidationError(
                "Le numéro de séance doit être supérieur ou égal à 1."
            )
        
        return numero_seance
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
        return instance


class ReeducationPerineeModalForm(ReeducationPerineeForm):
    """
    Formulaire modal HTMX pour les rééducations du périnée
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
                
                # Calculer automatiquement le prochain numéro de séance
                if not self.instance.pk:
                    last_seance = patient.reeducations_perinee.order_by('-numero_seance').first()
                    if last_seance:
                        self.fields['numero_seance'].initial = last_seance.numero_seance + 1
                        
            except Patient.DoesNotExist:
                pass
        
        # Ajuster les classes CSS pour le modal
        for field_name, field in self.fields.items():
            if field_name != 'patient':
                if hasattr(field.widget, 'attrs'):
                    current_class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = current_class.replace('focus:ring-blue-500', 'focus:ring-blue-500')


class ReeducationPerineeQuickForm(forms.ModelForm):
    """
    Formulaire rapide inline pour les rééducations du périnée
    Version simplifiée pour saisie rapide
    """
    
    class Meta:
        model = ReeducationPerinee
        fields = [
            'date_consultation',
            'numero_seance',
            'examen_clinique_travail',
            'a_prevoir'
        ]
        
        labels = {
            'date_consultation': 'Date',
            'numero_seance': 'N° séance',
            'examen_clinique_travail': 'Examen clinique / Travail',
            'a_prevoir': 'À prévoir',
        }
        
        widgets = {
            'date_consultation': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400',
                'max': date.today().isoformat()
            }),
            'numero_seance': NumberInput(attrs={
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400',
                'min': 1,
                'step': 1
            }),
            'examen_clinique_travail': Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400',
                'placeholder': 'Examen clinique et travail effectué...'
            }),
            'a_prevoir': Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400',
                'placeholder': 'Points à prévoir...'
            }),
        }
    
    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.patient = patient
        
        # Date par défaut aujourd'hui et calcul automatique du numéro de séance
        if not self.instance.pk:
            self.fields['date_consultation'].initial = date.today()
            
            # Calculer le prochain numéro de séance
            if self.patient:
                last_seance = self.patient.reeducations_perinee.order_by('-numero_seance').first()
                if last_seance:
                    self.fields['numero_seance'].initial = last_seance.numero_seance + 1
                else:
                    self.fields['numero_seance'].initial = 1
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        
        # Vérifier que le patient est bien une femme
        if self.patient and self.patient.type_patient != 'femme':
            raise forms.ValidationError(
                "Les séances de rééducation du périnée sont réservées aux femmes."
            )
        
        return cleaned_data
    
    def clean_date_consultation(self):
        """Validation de la date de consultation"""
        date_consultation = self.cleaned_data['date_consultation']
        
        if date_consultation and date_consultation > date.today():
            raise forms.ValidationError(
                "La date de la séance ne peut pas être dans le futur."
            )
        
        return date_consultation
    
    def clean_numero_seance(self):
        """Validation du numéro de séance"""
        numero_seance = self.cleaned_data['numero_seance']
        
        if numero_seance and numero_seance < 1:
            raise forms.ValidationError(
                "Le numéro de séance doit être supérieur ou égal à 1."
            )
        
        return numero_seance
    
    def save(self, commit=True):
        """Sauvegarde avec assignation du patient"""
        instance = super().save(commit=False)
        
        # Assigner le patient
        if self.patient:
            instance.patient = self.patient
        
        if commit:
            instance.save()
        
        return instance


class ReeducationPerineeSearchForm(forms.Form):
    """
    Formulaire de recherche pour les rééducations du périnée
    """
    
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Rechercher par nom, examen clinique...'
        }),
        label='Recherche'
    )
    
    date_debut = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Date de début'
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Date de fin'
    )
    
    numero_seance = forms.IntegerField(
        required=False,
        widget=NumberInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'min': 1,
            'placeholder': 'N° de séance'
        }),
        label='Numéro de séance'
    )