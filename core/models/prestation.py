from django.db import models
from django.core.exceptions import ValidationError


class Prestation(models.Model):
    """
    Modèle représentant une prestation pour les sages-femmes
    """
    
    ORIGINE_CHOICES = [
        ('', 'Vide'),
        ('LM', 'LM'),
        ('AT', 'AT'),
        ('MT', 'MT'),
        ('GP', 'GP'),
    ]
    
    # Relation avec le cadre d'exercice
    cadre_exercice = models.ForeignKey(
        'CadreExercice',
        on_delete=models.CASCADE,
        verbose_name="Cadre d'exercice",
        help_text="Cadre d'exercice associé à cette prestation"
    )
    
    # Désignation (obligatoire)
    designation = models.TextField(
        verbose_name="Désignation",
        help_text="Description de la prestation"
    )
    
    # Limite (facultatif)
    limite = models.TextField(
        blank=True,
        null=True,
        verbose_name="Limite",
        help_text="Limites ou contraintes de la prestation"
    )
    
    # Relation avec un acte unique
    acte = models.ForeignKey(
        'Acte',
        on_delete=models.CASCADE,
        verbose_name="Acte",
        help_text="Acte associé à cette prestation"
    )
    
    # Cotation (nombre)
    cotation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cotation",
        help_text="Valeur de cotation de la prestation"
    )
    
    # Entente préalable (obligatoire)
    entente_prealable = models.TextField(
        verbose_name="Entente préalable",
        help_text="Conditions d'entente préalable"
    )
    
    # Assurance maladie (facultatif)
    assurance_maladie = models.TextField(
        blank=True,
        null=True,
        verbose_name="Assurance maladie",
        help_text="Informations sur la prise en charge assurance maladie"
    )
    
    # Assurance maternité normale (facultatif)
    assurance_maternite_normale = models.TextField(
        blank=True,
        null=True,
        verbose_name="Assurance maternité normale",
        help_text="Informations sur la prise en charge maternité normale"
    )
    
    # Assurance maternité pathologie (facultatif)
    assurance_maternite_pathologie = models.TextField(
        blank=True,
        null=True,
        verbose_name="Assurance maternité pathologie",
        help_text="Informations sur la prise en charge maternité pathologique"
    )
    
    # Observation (facultatif)
    observation = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observation",
        help_text="Observations particulières"
    )
    
    # Suffixe (facultatif)
    suffixe = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Suffixe",
        help_text="Suffixe facultatif pour la prestation"
    )
    
    # Origine (liste avec choix)
    origine = models.CharField(
        max_length=2,
        choices=ORIGINE_CHOICES,
        blank=True,
        default='',
        verbose_name="Origine",
        help_text="Origine de la prestation"
    )
    
    # Actif (booléen)
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la prestation est active"
    )
    
    # Prescription (booléen)
    prescription = models.BooleanField(
        default=False,
        verbose_name="Prescription",
        help_text="Indique si une prescription est nécessaire"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "4. Prestation"
        verbose_name_plural = "4. Prestations"
        ordering = ['cadre_exercice__label', 'designation']
    
    def __str__(self):
        return f"{self.cadre_exercice.label} - {self.designation[:50]}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Valider que la cotation est positive
        if self.cotation is not None and self.cotation <= 0:
            raise ValidationError({
                'cotation': 'La cotation doit être un nombre positif.'
            })
    
    @property
    def acte_code(self):
        """Retourne le code de l'acte associé"""
        return self.acte.code if self.acte else "Aucun"
    
    @property
    def cotation_display(self):
        """Retourne la cotation formatée"""
        return f"{self.cotation} points" if self.cotation else "Non définie"
    
    @property
    def tarif(self):
        """Calcule le tarif en multipliant la cotation par le coût conventionnel actuel de l'acte"""
        if not self.cotation or not self.acte:
            return None
        
        cout_actuel = self.acte.cout_conventionnel_actuel
        if cout_actuel is None:
            return None
            
        return float(self.cotation) * float(cout_actuel)
    
    @property
    def tarif_display(self):
        """Retourne le tarif formaté"""
        tarif = self.tarif
        if tarif is None:
            return "Non calculable"
        return f"{tarif:.0f} XPF"