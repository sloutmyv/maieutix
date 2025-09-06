"""
Formulaires pour les consultations gynécologiques
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from core.models import ConsultationGynecologique, Patient


class ConsultationGynecologiqueForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une consultation gynécologique
    """
    
    class Meta:
        model = ConsultationGynecologique
        fields = [
            'patient',
            'date_consultation',
            'tension_systolique',
            'tension_diastolique', 
            'poids',
            'motif',
            'examen',
            'prescription',
            'notes'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'date_consultation': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'max': date.today().isoformat()
            }),
            'tension_systolique': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Ex: 120',
                'min': '80',
                'max': '250'
            }),
            'tension_diastolique': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Ex: 80',
                'min': '40',
                'max': '150'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Ex: 65.5',
                'min': '30',
                'max': '200',
                'step': '0.1'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 3,
                'placeholder': 'Motif de la consultation...'
            }),
            'examen': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 4,
                'placeholder': 'Résultats de l\'examen clinique...'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 3,
                'placeholder': 'Prescription médicamenteuse ou recommandations...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'rows': 2,
                'placeholder': 'Notes complémentaires...'
            })
        }
        
        labels = {
            'patient': 'Patiente',
            'date_consultation': 'Date de consultation',
            'tension_systolique': 'Tension systolique (mmHg)',
            'tension_diastolique': 'Tension diastolique (mmHg)',
            'poids': 'Poids (kg)',
            'motif': 'Motif de la consultation',
            'examen': 'Examen clinique',
            'prescription': 'Prescription',
            'notes': 'Notes complémentaires'
        }
        
        help_texts = {
            'date_consultation': 'Date de la consultation (par défaut aujourd\'hui)',
            'tension_systolique': 'Tension artérielle systolique (80-250 mmHg)',
            'tension_diastolique': 'Tension artérielle diastolique (40-150 mmHg)',
            'poids': 'Poids de la patiente en kilogrammes (30-200 kg)',
            'motif': 'Raison de la venue de la patiente',
            'examen': 'Résultats de l\'examen gynécologique',
            'prescription': 'Prescription médicamenteuse ou recommandations',
            'notes': 'Notes additionnelles sur la consultation'
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer la patiente si passée en paramètre
        self.patient_id = kwargs.pop('patient_id', None)
        super().__init__(*args, **kwargs)
        
        # Si une patiente spécifique est fournie, limiter les choix
        if self.patient_id:
            try:
                patient = Patient.objects.get(pk=self.patient_id)
                self.fields['patient'].queryset = Patient.objects.filter(pk=self.patient_id)
                self.fields['patient'].initial = patient
                self.fields['patient'].widget.attrs['readonly'] = True
            except Patient.DoesNotExist:
                pass
        else:
            # Limiter aux patientes femmes uniquement
            self.fields['patient'].queryset = Patient.objects.filter(
                type_patient='femme'
            ).order_by('nom', 'prenom')
        
        # Définir la date max à aujourd'hui
        today = date.today().isoformat()
        self.fields['date_consultation'].widget.attrs['max'] = today
        
        # Marquer les champs obligatoires
        required_fields = ['patient', 'date_consultation', 'motif']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                
        # Rendre les champs de tension optionnels mais liés
        self.fields['tension_systolique'].required = False
        self.fields['tension_diastolique'].required = False
        self.fields['poids'].required = False
        
    def clean_date_consultation(self):
        """Validation de la date de consultation"""
        date_consultation = self.cleaned_data.get('date_consultation')
        
        if date_consultation and date_consultation > date.today():
            raise ValidationError("La date de consultation ne peut pas être dans le futur.")
        
        return date_consultation
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        
        tension_systolique = cleaned_data.get('tension_systolique')
        tension_diastolique = cleaned_data.get('tension_diastolique')
        patient = cleaned_data.get('patient')
        
        # Validation de la tension artérielle
        if tension_systolique and tension_diastolique:
            if tension_systolique <= tension_diastolique:
                raise ValidationError({
                    'tension_systolique': 'La tension systolique doit être supérieure à la tension diastolique.'
                })
        
        # Validation cohérence: si une tension est renseignée, l'autre doit l'être aussi
        if (tension_systolique and not tension_diastolique) or \
           (tension_diastolique and not tension_systolique):
            raise ValidationError(
                'La tension artérielle doit être complète (systolique ET diastolique).'
            )
        
        # Vérifier que la patiente est bien une femme
        if patient and patient.type_patient != 'femme':
            raise ValidationError({
                'patient': 'Les consultations gynécologiques sont réservées aux femmes.'
            })
        
        return cleaned_data


class ConsultationGynecologiqueModalForm(ConsultationGynecologiqueForm):
    """
    Formulaire spécialisé pour le modal de consultation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajuster les classes CSS pour le modal
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                current_class = field.widget.attrs.get('class', '')
                # Ajouter des classes spécifiques au modal si nécessaire
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = current_class.replace(
                        'focus:ring-primary focus:border-primary',
                        'focus:ring-blue-500 focus:border-blue-500'
                    )
        
        # Pour le modal, cacher le champ patient car il sera fourni via le contexte
        if 'patient' in self.fields and self.patient_id:
            self.fields['patient'].widget = forms.HiddenInput()


class ConsultationGynecologiqueQuickForm(forms.ModelForm):
    """
    Formulaire complet pour ajouter une consultation inline
    """
    
    class Meta:
        model = ConsultationGynecologique
        fields = [
            'date_consultation',
            'tension_systolique',
            'tension_diastolique', 
            'poids',
            'motif',
            'examen',
            'prescription',
            'notes'
        ]
        
        widgets = {
            'date_consultation': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-8',
            }),
            'tension_systolique': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-8',
                'placeholder': '120',
                'min': '80',
                'max': '250'
            }),
            'tension_diastolique': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-8',
                'placeholder': '80',
                'min': '40',
                'max': '150'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-8',
                'placeholder': '65.5',
                'step': '0.1',
                'min': '30',
                'max': '200'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
                'style': 'height: 88px;',
                'placeholder': 'Motif de la consultation...'
            }),
            'examen': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-16',
                'placeholder': 'Résultats de l\'examen gynécologique...'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-16',
                'placeholder': 'Prescription médicamenteuse ou recommandations...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 h-16',
                'placeholder': 'Notes additionnelles...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        
        # Définir la date par défaut à aujourd'hui
        if not self.instance.pk:
            self.fields['date_consultation'].initial = date.today()
        
        # Tous les champs sont optionnels sauf le motif
        for field_name in self.fields:
            if field_name != 'motif':
                self.fields[field_name].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Associer la patiente
        if self.patient:
            instance.patient = self.patient
        
        if commit:
            instance.save()
            
        return instance