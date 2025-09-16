"""
Modèle pour la rééducation du périnée
"""

from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

from .patient import Patient
from .sagefemme import SageFemme


class ReeducationPerinee(models.Model):
    """
    Modèle pour les séances de rééducation du périnée
    
    Similaire aux consultations de préparation à la naissance mais spécialisé pour
    la rééducation du périnée avec numéro de séance et examen clinique.
    """
    
    # Relations
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='reeducations_perinee',
        verbose_name="Patiente"
    )
    
    created_by = models.ForeignKey(
        SageFemme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reeducations_perinee_creees',
        verbose_name="Sage-femme créatrice"
    )
    
    # Informations de la séance
    date_consultation = models.DateField(
        verbose_name="Date de la séance",
        default=date.today,
        help_text="Date de la séance de rééducation du périnée"
    )
    
    numero_seance = models.PositiveIntegerField(
        verbose_name="Numéro de séance",
        default=1,
        help_text="Numéro de la séance (commence à 1)"
    )
    
    # Contenu spécifique rééducation du périnée
    examen_clinique_travail = models.TextField(
        verbose_name="Examen clinique / Travail de rééducation",
        help_text="Examen clinique effectué et travail de rééducation réalisé lors de la séance",
        blank=True
    )
    
    a_prevoir = models.TextField(
        verbose_name="À prévoir",
        help_text="Points à prévoir pour la prochaine séance ou recommandations",
        blank=True
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "6.1.6 Rééducation du Périnée"
        verbose_name_plural = "6.1.6 Rééducations du Périnée"
        ordering = ['-date_consultation', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'date_consultation']),
            models.Index(fields=['created_by', 'date_consultation']),
            models.Index(fields=['date_consultation']),
            models.Index(fields=['numero_seance']),
        ]
    
    def __str__(self):
        """Représentation textuelle de la séance de rééducation"""
        return f"Rééducation périnée - {str(self.patient)} - Séance {self.numero_seance} du {self.date_consultation.strftime('%d/%m/%Y')}"
    
    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Validation : la date ne peut pas être dans le futur
        if self.date_consultation and self.date_consultation > date.today():
            raise ValidationError({
                'date_consultation': 'La date de la séance ne peut pas être dans le futur.'
            })
        
        # Validation : seules les femmes peuvent avoir des séances de rééducation du périnée
        # SEULEMENT si le patient est déjà assigné (pour éviter l'erreur lors de la validation du formulaire)
        if hasattr(self, 'patient') and self.patient_id and self.patient and self.patient.type_patient != 'femme':
            raise ValidationError({
                'patient': 'Les séances de rééducation du périnée sont réservées aux femmes.'
            })
        
        # Validation : le numéro de séance doit être positif
        if self.numero_seance and self.numero_seance < 1:
            raise ValidationError({
                'numero_seance': 'Le numéro de séance doit être supérieur ou égal à 1.'
            })
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec validation"""
        # Validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    @property
    def seance_resume(self):
        """Résumé de la séance pour l'affichage"""
        resume_parts = []
        
        if self.examen_clinique_travail:
            resume_parts.append(f"Examen: {self.examen_clinique_travail[:100]}")
        
        if self.a_prevoir:
            resume_parts.append(f"À prévoir: {self.a_prevoir[:100]}")
        
        if resume_parts:
            return " | ".join(resume_parts)
        
        return f"Séance de rééducation du périnée n°{self.numero_seance}"
    
    @property
    def numero_seance_affichage(self):
        """Retourne le numéro de séance pour l'affichage avec format stylé"""
        return f"Séance {self.numero_seance}"