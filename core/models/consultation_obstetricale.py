"""
Modèle ConsultationObstetricale pour la gestion des consultations obstétricales
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


class ConsultationObstetricale(models.Model):
    """
    Consultation obstétricale d'une patiente
    
    Enregistre les données d'une consultation obstétricale incluant
    les constantes vitales, le motif, l'examen et la prescription.
    """
    
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='consultations_obstetricales',
        verbose_name="Patiente"
    )
    
    # Date de la consultation
    date_consultation = models.DateField(
        verbose_name="Date de consultation",
        default=date.today,
        help_text="Date de la consultation (par défaut aujourd'hui)"
    )
    
    # Constantes vitales
    tension_systolique = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(80), MaxValueValidator(250)],
        verbose_name="Tension systolique (mmHg)",
        help_text="Tension artérielle systolique en mmHg (80-250)"
    )
    
    tension_diastolique = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(40), MaxValueValidator(150)],
        verbose_name="Tension diastolique (mmHg)",
        help_text="Tension artérielle diastolique en mmHg (40-150)"
    )
    
    poids = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(30.0), MaxValueValidator(200.0)],
        verbose_name="Poids (kg)",
        help_text="Poids de la patiente en kilogrammes (30-200 kg)"
    )
    
    # Motif de consultation
    motif = models.TextField(
        verbose_name="Motif de la consultation",
        help_text="Raison de la venue de la patiente"
    )
    
    # Examen clinique
    examen = models.TextField(
        blank=True,
        verbose_name="Examen clinique",
        help_text="Résultats de l'examen obstétrical"
    )
    
    # Prescription
    prescription = models.TextField(
        blank=True,
        verbose_name="Prescription",
        help_text="Prescription médicamenteuse ou recommandations"
    )
    
    # SA (Semaines d'Aménorrhée)
    semaines_amenorrhee = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="SA (Semaines d'Aménorrhée)",
        help_text="Semaines d'aménorrhée au moment de la consultation (calculé automatiquement)"
    )
    
    # Notes additionnelles
    notes = models.TextField(
        blank=True,
        verbose_name="Notes complémentaires",
        help_text="Notes additionnelles sur la consultation"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        'core.SageFemme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Créé par",
        help_text="Sage-femme qui a créé la consultation"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )
    
    class Meta:
        verbose_name = "6.1.3.2 Consultation Obstétricale"
        verbose_name_plural = "6.1.3.2 Consultations Obstétricales"
        ordering = ['-date_consultation', '-created_at']
        
    def __str__(self):
        return f"Consultation du {self.date_consultation.strftime('%d/%m/%Y')} - {self.patient.nom_complet}"
    
    def clean(self):
        """
        Validation du modèle
        """
        super().clean()
        
        # Vérifier que la date de consultation n'est pas dans le futur
        if self.date_consultation and self.date_consultation > date.today():
            raise ValidationError({
                'date_consultation': 'La date de consultation ne peut pas être dans le futur.'
            })
        
        # Validation de la tension artérielle
        if self.tension_systolique and self.tension_diastolique:
            if self.tension_systolique <= self.tension_diastolique:
                raise ValidationError({
                    'tension_systolique': 'La tension systolique doit être supérieure à la tension diastolique.'
                })
        
        # Validation cohérence: si une tension est renseignée, l'autre doit l'être aussi
        if (self.tension_systolique and not self.tension_diastolique) or \
           (self.tension_diastolique and not self.tension_systolique):
            raise ValidationError({
                '__all__': 'La tension artérielle doit être complète (systolique ET diastolique).'
            })
    
    @property
    def tension_complete(self):
        """
        Retourne la tension artérielle complète formatée
        """
        if self.tension_systolique and self.tension_diastolique:
            return f"{self.tension_systolique}/{self.tension_diastolique} mmHg"
        return None
    
    @property
    def tension_interpretation(self):
        """
        Interprétation de la tension artérielle selon les normes
        """
        if not (self.tension_systolique and self.tension_diastolique):
            return None
        
        sys = self.tension_systolique
        dia = self.tension_diastolique
        
        if sys < 120 and dia < 80:
            return "Tension normale"
        elif sys < 130 and dia < 80:
            return "Tension normale haute"
        elif (130 <= sys < 140) or (80 <= dia < 90):
            return "Hypertension stade 1"
        elif (140 <= sys < 180) or (90 <= dia < 120):
            return "Hypertension stade 2"
        elif sys >= 180 or dia >= 120:
            return "Crise hypertensive"
        else:
            return "À évaluer"
    
    @property
    def imc(self):
        """
        Calcul de l'IMC si le poids est disponible et qu'il y a des antécédents avec taille
        """
        if not self.poids:
            return None
        
        # Chercher la taille dans les antécédents de la patiente
        try:
            antecedents = self.patient.antecedents
            if antecedents and antecedents.taille:
                return round(self.poids / (antecedents.taille ** 2), 1)
        except:
            pass
        
        return None
    
    @property
    def resume_consultation(self):
        """
        Résumé court de la consultation pour affichage
        """
        resume = f"Motif: {self.motif[:50]}"
        if len(self.motif) > 50:
            resume += "..."
        
        if self.tension_complete:
            resume += f" - TA: {self.tension_complete}"
        
        if self.poids:
            resume += f" - Poids: {self.poids}kg"
            
        return resume
    
    def calculer_sa(self):
        """
        Calcule les semaines d'aménorrhée à la date de consultation
        """
        try:
            # Vérifier que tous les éléments nécessaires sont présents
            if not (self.patient_id and self.date_consultation):
                return None
                
            # Accéder au patient de manière sécurisée
            patient = getattr(self, 'patient', None)
            if not patient:
                return None
                
            if (patient.type_patient == 'femme' and 
                patient.date_debut_grossesse):
                
                delta = self.date_consultation - patient.date_debut_grossesse
                jours_grossesse = delta.days
                
                if jours_grossesse < 0:
                    return "Grossesse pas encore commencée"
                
                semaines = jours_grossesse // 7
                jours_reste = jours_grossesse % 7
                
                if semaines == 0:
                    if jours_reste == 0:
                        return "Début de grossesse"
                    elif jours_reste == 1:
                        return "1 jour"
                    else:
                        return f"{jours_reste} jours"
                elif semaines == 1:
                    if jours_reste == 0:
                        return "1 SA"
                    elif jours_reste == 1:
                        return "1 SA + 1j"
                    else:
                        return f"1 SA + {jours_reste}j"
                else:
                    if jours_reste == 0:
                        return f"{semaines} SA"
                    elif jours_reste == 1:
                        return f"{semaines} SA + 1j"
                    else:
                        return f"{semaines} SA + {jours_reste}j"
        except Exception:
            # En cas d'erreur, retourner None silencieusement
            pass
            
        return None

    def save(self, *args, **kwargs):
        """Validation et calcul automatique de la SA avant sauvegarde"""
        # Calculer automatiquement la SA
        sa_calculee = self.calculer_sa()
        if sa_calculee:
            self.semaines_amenorrhee = sa_calculee
        
        self.full_clean()
        super().save(*args, **kwargs)