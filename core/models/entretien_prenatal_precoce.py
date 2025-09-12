from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .patient import Patient
from .sagefemme import SageFemme


class EntretienPrenatalPrecoce(models.Model):
    """
    Modèle pour l'entretien prénatal précoce
    Entretien obligatoire entre la 4e et 6e mois de grossesse
    """
    
    # Relations
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='entretiens_prenataux_precoces',
        verbose_name="Patiente",
        limit_choices_to={'type_patient': 'femme'}
    )
    
    sage_femme = models.ForeignKey(
        SageFemme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entretiens_prenataux_precoces',
        verbose_name="Sage-femme"
    )
    
    # Informations générales
    date_entretien = models.DateField(
        verbose_name="Date de l'entretien",
        help_text="Date de réalisation de l'entretien prénatal précoce"
    )
    
    semaines_amenorrhee = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="SA à la date de l'entretien",
        help_text="Semaines d'aménorrhée calculées automatiquement"
    )
    
    conjoint_present = models.BooleanField(
        default=False,
        verbose_name="Conjoint présent",
        help_text="Le conjoint/partenaire était-il présent lors de l'entretien ?"
    )
    
    lieu_accouchement_prevu = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Lieu d'accouchement prévu",
        help_text="Maternité, clinique ou lieu prévu pour l'accouchement"
    )
    
    # Contenus de l'entretien
    atcd_marquants_sante = models.TextField(
        blank=True,
        verbose_name="ATCD marquants et santé globale",
        help_text="Antécédents marquants et état de santé général"
    )
    
    environnement_social_familial = models.TextField(
        blank=True,
        verbose_name="Environnement social et familial",
        help_text="Contexte socio-familial, soutien, conditions de vie"
    )
    
    projet_naissance_parentalite = models.TextField(
        blank=True,
        verbose_name="Projet de naissance et de parentalité",
        help_text="Projet de naissance et préparation à la parentalité"
    )
    
    ressenti = models.TextField(
        blank=True,
        verbose_name="Ressenti",
        help_text="Ressenti de la patiente et du conjoint sur la grossesse"
    )
    
    propositions_liens = models.TextField(
        blank=True,
        verbose_name="Propositions/liens",
        help_text="Orientations, propositions d'accompagnement, liens vers ressources"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    created_by = models.ForeignKey(
        SageFemme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entretiens_crees',
        verbose_name="Créé par"
    )
    
    class Meta:
        verbose_name = "6.1.4 Entretien Prénatal Précoce"
        verbose_name_plural = "6.1.4 Entretiens Prénataux Précoces"
        ordering = ['-date_entretien', '-created_at']
        indexes = [
            models.Index(fields=['-date_entretien']),
            models.Index(fields=['patient', '-date_entretien']),
        ]
    
    def __str__(self):
        return f"EPP du {self.date_entretien.strftime('%d/%m/%Y')} - {self.patient.nom_complet}"
    
    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Vérifier que la patiente est bien une femme
        if self.patient_id and self.patient.type_patient != 'femme':
            raise ValidationError("L'entretien prénatal précoce est réservé aux femmes.")
        
        # Vérifier que la date d'entretien n'est pas dans le futur
        if self.date_entretien and self.date_entretien > date.today():
            raise ValidationError("La date de l'entretien ne peut pas être dans le futur.")
        
        # Vérifier que la patiente a une DDG définie
        if self.patient_id and not self.patient.date_debut_grossesse:
            raise ValidationError("La patiente doit avoir une date de début de grossesse définie.")
        
        # Vérifier que l'entretien a lieu après le début de grossesse
        if (self.patient_id and self.patient.date_debut_grossesse and 
            self.date_entretien and self.date_entretien < self.patient.date_debut_grossesse):
            raise ValidationError("La date de l'entretien doit être postérieure au début de grossesse.")
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec calcul automatique de la SA"""
        # Calculer la SA avant sauvegarde
        if not self.semaines_amenorrhee and self.date_entretien and self.patient_id:
            self.semaines_amenorrhee = self.calculer_sa()
        
        # Validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def calculer_sa(self):
        """
        Calcule les semaines d'aménorrhée à la date de l'entretien
        Retourne une chaîne formatée ou vide si calcul impossible
        """
        try:
            # Vérifier que nous avons les données nécessaires
            if not (self.patient_id and self.date_entretien):
                return ""
            
            # Accès sécurisé au patient
            patient = getattr(self, 'patient', None)
            if not patient:
                # Si pas encore chargé, essayer de le récupérer
                if hasattr(self, 'patient_id'):
                    try:
                        from .patient import Patient
                        patient = Patient.objects.get(pk=self.patient_id)
                    except Patient.DoesNotExist:
                        return ""
                else:
                    return ""
            
            # Vérifier que c'est une femme avec DDG
            if patient.type_patient != 'femme' or not patient.date_debut_grossesse:
                return ""
            
            # Calculer la différence en jours
            delta = self.date_entretien - patient.date_debut_grossesse
            jours_grossesse = delta.days
            
            # Si négatif, la grossesse n'a pas encore commencé
            if jours_grossesse < 0:
                return "Grossesse pas encore commencée"
            
            # Calculer les semaines et jours
            semaines = jours_grossesse // 7
            jours_restants = jours_grossesse % 7
            
            # Formater le résultat
            if jours_restants == 0:
                return f"{semaines} SA"
            else:
                return f"{semaines} SA + {jours_restants}j"
                
        except Exception:
            # En cas d'erreur, retourner une chaîne vide
            return ""
    
    @property
    def sa_affichage_court(self):
        """Version courte de l'affichage SA pour les listes"""
        if self.semaines_amenorrhee:
            return self.semaines_amenorrhee
        return "-"
    
    @property
    def entretien_resume(self):
        """Résumé de l'entretien pour affichage"""
        elements = []
        
        if self.lieu_accouchement_prevu:
            elements.append(f"Lieu: {self.lieu_accouchement_prevu}")
        
        if self.conjoint_present:
            elements.append("Conjoint présent")
        
        if self.semaines_amenorrhee:
            elements.append(f"SA: {self.semaines_amenorrhee}")
        
        return " • ".join(elements) if elements else "Entretien prénatal précoce"
    
    @property
    def est_dans_periode_optimale(self):
        """
        Vérifie si l'entretien a lieu dans la période optimale (16-28 SA)
        """
        if not self.semaines_amenorrhee:
            return None
        
        try:
            # Extraire le nombre de semaines
            if 'SA' in self.semaines_amenorrhee:
                semaines_str = self.semaines_amenorrhee.split('SA')[0].strip()
                if '+' in semaines_str:
                    semaines_str = semaines_str.split('+')[0].strip()
                
                semaines = int(semaines_str)
                return 16 <= semaines <= 28
        except (ValueError, AttributeError):
            pass
        
        return None
    
    @property
    def indicateur_periode(self):
        """Indicateur coloré pour la période de l'entretien"""
        est_optimal = self.est_dans_periode_optimale
        
        if est_optimal is True:
            return "optimal"  # Vert
        elif est_optimal is False:
            return "limite"   # Orange
        else:
            return "inconnu"  # Gris