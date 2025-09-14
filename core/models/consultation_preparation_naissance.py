"""
Modèle pour les consultations de préparation à la naissance
"""

from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

from .patient import Patient
from .sagefemme import SageFemme


class ConsultationPreparationNaissance(models.Model):
    """
    Modèle pour les consultations de préparation à la naissance
    
    Similaire aux consultations gynécologiques mais spécialisé pour
    la préparation à la naissance avec thèmes abordés et points à prévoir.
    """
    
    # Relations
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consultations_preparation_naissance',
        verbose_name="Patiente"
    )
    
    created_by = models.ForeignKey(
        SageFemme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations_preparation_naissance_creees',
        verbose_name="Sage-femme créatrice"
    )
    
    # Informations de la consultation
    date_consultation = models.DateField(
        verbose_name="Date de consultation",
        default=date.today,
        help_text="Date de la consultation de préparation à la naissance"
    )
    
    semaines_amenorrhee = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Semaines d'aménorrhée",
        help_text="Calculées automatiquement à partir de la DDG"
    )
    
    # Contenu spécifique préparation à la naissance
    theme_aborde = models.TextField(
        verbose_name="Thème(s) abordé(s)",
        help_text="Thème(s) principal(aux) abordé(s) lors de la consultation",
        blank=True
    )
    
    a_prevoir = models.TextField(
        verbose_name="À prévoir",
        help_text="Points à prévoir pour la prochaine consultation ou l'accouchement",
        blank=True
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "6.1.5 Consultation Préparation à la Naissance"
        verbose_name_plural = "6.1.5 Consultations Préparation à la Naissance"
        ordering = ['-date_consultation', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'date_consultation']),
            models.Index(fields=['created_by', 'date_consultation']),
            models.Index(fields=['date_consultation']),
        ]
    
    def __str__(self):
        """Représentation textuelle de la consultation"""
        return f"Préparation naissance - {str(self.patient)} du {self.date_consultation.strftime('%d/%m/%Y')}"
    
    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Validation : la date ne peut pas être dans le futur
        if self.date_consultation and self.date_consultation > date.today():
            raise ValidationError({
                'date_consultation': 'La date de consultation ne peut pas être dans le futur.'
            })
        
        # Validation : seules les femmes peuvent avoir des consultations de préparation à la naissance
        # SEULEMENT si le patient est déjà assigné (pour éviter l'erreur lors de la validation du formulaire)
        if hasattr(self, 'patient') and self.patient_id and self.patient and self.patient.type_patient != 'femme':
            raise ValidationError({
                'patient': 'Les consultations de préparation à la naissance sont réservées aux femmes.'
            })
        
        # Validation : la patiente doit avoir une DDG pour calculer les SA
        if hasattr(self, 'patient') and self.patient_id and self.patient and self.patient.type_patient == 'femme' and not self.patient.date_debut_grossesse:
            # On accepte mais on ne peut pas calculer les SA
            pass
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec calcul automatique des SA"""
        # Calculer les SA automatiquement si la patiente a une DDG
        if self.patient and self.patient.date_debut_grossesse:
            self.semaines_amenorrhee = self.calculer_semaines_amenorrhee()
        
        # Validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def calculer_semaines_amenorrhee(self):
        """
        Calcule les semaines d'aménorrhée à partir de la DDG
        Format : "XX SA" ou "XX SA + Yj"
        """
        try:
            if not self.patient or not self.patient.date_debut_grossesse:
                return None
        except:
            return None
        
        # Calcul des jours écoulés depuis la DDG
        jours_ecoules = (self.date_consultation - self.patient.date_debut_grossesse).days
        
        if jours_ecoules < 0:
            return "DDG postérieure"
        
        # Conversion en semaines et jours
        semaines_completes = jours_ecoules // 7
        jours_restants = jours_ecoules % 7
        
        if jours_restants == 0:
            return f"{semaines_completes} SA"
        else:
            return f"{semaines_completes} SA + {jours_restants}j"
    
    @property
    def consultation_resume(self):
        """Résumé de la consultation pour l'affichage"""
        resume_parts = []
        
        if self.theme_aborde:
            resume_parts.append(f"Thème: {self.theme_aborde[:100]}")
        
        if self.a_prevoir:
            resume_parts.append(f"À prévoir: {self.a_prevoir[:100]}")
        
        if resume_parts:
            return " | ".join(resume_parts)
        
        return "Consultation de préparation à la naissance"
    
    @property
    def sa_affichage(self):
        """Retourne les SA pour l'affichage avec format stylé"""
        return self.semaines_amenorrhee or "SA non calculées"