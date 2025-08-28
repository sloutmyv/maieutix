from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Acte(models.Model):
    """
    Modèle représentant un type d'acte
    """
    
    # Code de l'acte (texte court)
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code acte",
        help_text="Code court identifiant l'acte (ex: CSF, VGC, etc.)"
    )
    
    # Libellé de l'acte (description)
    libelle = models.TextField(
        verbose_name="Libellé",
        help_text="Description complète de l'acte"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "3. Acte"
        verbose_name_plural = "3. Actes"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle[:50]}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Valider que le code ne contient pas d'espaces
        if ' ' in self.code:
            raise ValidationError({
                'code': 'Le code ne doit pas contenir d\'espaces.'
            })
    
    @property
    def tarif_actuel(self):
        """
        Retourne le tarif actuellement valide pour cet acte
        """
        return self.tarifs_periodes.filter(
            date_debut__lte=timezone.now().date()
        ).filter(
            models.Q(date_fin__isnull=True) | 
            models.Q(date_fin__gte=timezone.now().date())
        ).first()
    
    @property
    def cout_conventionnel_actuel(self):
        """
        Retourne le coût conventionnel actuel en XPF
        """
        tarif = self.tarif_actuel
        return tarif.cout_xpf if tarif else None


class TarifPeriode(models.Model):
    """
    Modèle représentant un tarif pour un acte sur une période donnée
    """
    
    # Relation avec l'acte
    acte = models.ForeignKey(
        Acte,
        on_delete=models.CASCADE,
        related_name='tarifs_periodes',
        verbose_name="Acte"
    )
    
    # Coût conventionnel en XPF
    cout_xpf = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Coût conventionnel (XPF)",
        help_text="Montant en francs CFP"
    )
    
    # Période de validité
    date_debut = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de validité du tarif"
    )
    
    date_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin de validité (laisser vide pour un tarif permanent)"
    )
    
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "3.1 Tarif Acte"
        verbose_name_plural = "3.1 Tarifs Actes"
        ordering = ['-date_debut']
        
        # Contrainte pour éviter les chevauchements de périodes pour un même acte
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=models.F('date_debut')),
                name='date_fin_apres_date_debut'
            )
        ]
    
    def __str__(self):
        if self.date_fin:
            periode = f"du {self.date_debut} au {self.date_fin}"
        else:
            periode = f"à partir du {self.date_debut}"
        return f"{self.acte.code} - {self.cout_xpf} XPF ({periode})"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Valider que la date de fin est après la date de début
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError({
                'date_fin': 'La date de fin doit être postérieure à la date de début.'
            })
        
        # Valider qu'il n'y a pas de chevauchement avec d'autres périodes du même acte
        if self.acte_id:
            overlapping_periods = TarifPeriode.objects.filter(acte=self.acte).exclude(pk=self.pk)
            
            for periode in overlapping_periods:
                if self._periods_overlap(periode):
                    raise ValidationError({
                        '__all__': f'Cette période chevauche avec une période existante : {periode}'
                    })
    
    def _periods_overlap(self, other_period):
        """
        Vérifie si cette période chevauche avec une autre période
        """
        # Cas 1: Cette période commence avant que l'autre se termine
        if self.date_debut <= (other_period.date_fin or timezone.now().date().replace(year=9999)):
            # Cas 2: Cette période se termine après que l'autre commence
            if (self.date_fin or timezone.now().date().replace(year=9999)) >= other_period.date_debut:
                return True
        return False
    
    @property
    def est_actuel(self):
        """
        Vérifie si cette période tarifaire est actuellement valide
        """
        aujourd_hui = timezone.now().date()
        return (
            self.date_debut <= aujourd_hui and 
            (self.date_fin is None or self.date_fin >= aujourd_hui)
        )
    
    @property
    def statut(self):
        """
        Retourne le statut de la période (Futur, Actuel, Expiré)
        """
        aujourd_hui = timezone.now().date()
        
        if self.date_debut > aujourd_hui:
            return "Futur"
        elif self.date_fin and self.date_fin < aujourd_hui:
            return "Expiré"
        else:
            return "Actuel"