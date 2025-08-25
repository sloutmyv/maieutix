"""
Modèle PeriodeActivite pour la gestion des périodes d'activité des sages-femmes
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


class PeriodeActivite(models.Model):
    """
    Période d'activité d'une sage-femme
    
    Gère les périodes d'activité avec date de début obligatoire et date de fin facultative.
    Quand la date de fin est dépassée, la sage-femme devient inactive.
    Sans date de fin, la période est considérée comme en cours.
    """
    
    sage_femme = models.ForeignKey(
        'SageFemme',
        on_delete=models.CASCADE,
        related_name='periodes_activite',
        verbose_name="Sage-femme"
    )
    
    date_debut = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de la période d'activité (obligatoire)"
    )
    
    date_fin = models.DateField(
        verbose_name="Date de fin",
        blank=True,
        null=True,
        help_text="Date de fin de la période d'activité (facultative). Si vide, la période est considérée comme en cours."
    )
    
    commentaire = models.TextField(
        verbose_name="Commentaire",
        blank=True,
        help_text="Commentaire sur cette période d'activité"
    )
    
    class Meta:
        verbose_name = "2.1 Période d'activité"
        verbose_name_plural = "2.1 Périodes d'activité"
        ordering = ['-date_debut']
        
    def __str__(self):
        nom_complet = f"{self.sage_femme.prenom} {self.sage_femme.nom}"
        
        if self.date_fin:
            return f"{nom_complet} - Du {self.date_debut.strftime('%d/%m/%Y')} au {self.date_fin.strftime('%d/%m/%Y')}"
        return f"{nom_complet} - Du {self.date_debut.strftime('%d/%m/%Y')} (en cours)"
    
    def clean(self):
        """
        Validation du modèle
        """
        super().clean()
        
        # Vérifier que la date de fin n'est pas antérieure à la date de début
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError({
                'date_fin': 'La date de fin ne peut pas être antérieure à la date de début.'
            })
        
        # Vérifications spécifiques à la sage-femme
        if self.sage_femme_id:
            periodes_existantes = PeriodeActivite.objects.filter(
                sage_femme=self.sage_femme
            ).exclude(pk=self.pk)
            
            # Vérifier s'il existe déjà une période ouverte (sans date de fin)
            periode_ouverte = periodes_existantes.filter(date_fin__isnull=True).first()
            if periode_ouverte:
                if not self.date_fin:
                    # Nouvelle période sans fin alors qu'une période ouverte existe
                    raise ValidationError({
                        '__all__': f'Une période en cours existe déjà depuis le {periode_ouverte.date_debut}. '
                                  'Vous devez d\'abord fermer cette période en définissant une date de fin.'
                    })
                else:
                    # Nouvelle période avec fin, mais une période ouverte existe
                    # Vérifier que la nouvelle période ne chevauche pas avec la période ouverte
                    if self._periodes_se_chevauchent(periode_ouverte):
                        raise ValidationError({
                            '__all__': f'Cette période chevauche avec la période ouverte existante depuis le {periode_ouverte.date_debut}. '
                                      'Vous devez d\'abord fermer la période ouverte.'
                        })
            
            # Si on modifie une période existante qui était ouverte pour lui ajouter une date de fin
            if self.pk and self.date_fin:
                # Vérifier qu'on ne crée pas de chevauchement en fermant cette période
                autres_periodes = periodes_existantes.exclude(pk=self.pk)
                for periode in autres_periodes:
                    if self._periodes_se_chevauchent(periode):
                        raise ValidationError({
                            'date_fin': f'La date de fin choisie crée un chevauchement avec la période: {periode}'
                        })
            
            # Vérifier qu'il n'y a pas de chevauchement avec d'autres périodes fermées
            for periode in periodes_existantes:
                if self._periodes_se_chevauchent(periode):
                    if not periode.date_fin:
                        # Cas déjà traité ci-dessus
                        continue
                    raise ValidationError({
                        '__all__': f'Cette période chevauche avec une période existante: {periode}'
                    })
    
    def _periodes_se_chevauchent(self, autre_periode):
        """
        Vérifie si cette période chevauche avec une autre période
        """
        # Si l'autre période n'a pas de fin, elle est active indéfiniment
        autre_fin = autre_periode.date_fin or date.max
        # Si cette période n'a pas de fin, elle est active indéfiniment
        cette_fin = self.date_fin or date.max
        
        # Vérification du chevauchement
        return (
            self.date_debut <= autre_fin and
            cette_fin >= autre_periode.date_debut
        )
    
    @property
    def est_active(self):
        """
        Détermine si cette période d'activité est actuellement active
        """
        aujourd_hui = timezone.now().date()
        
        # La période doit avoir commencé
        if self.date_debut > aujourd_hui:
            return False
        
        # Si pas de date de fin, la période est active
        if not self.date_fin:
            return True
        
        # Si la date de fin n'est pas dépassée, la période est active
        return self.date_fin >= aujourd_hui
    
    @property
    def est_en_cours(self):
        """
        Alias pour est_active pour plus de clarté
        """
        return self.est_active
    
    @property
    def duree_jours(self):
        """
        Calcule la durée de la période en jours
        """
        if not self.date_fin:
            # Période en cours, calculer depuis le début jusqu'à aujourd'hui
            return (timezone.now().date() - self.date_debut).days
        
        return (self.date_fin - self.date_debut).days
    
    @property
    def statut_display(self):
        """
        Retourne un statut lisible pour l'affichage
        """
        if self.est_active:
            if self.date_fin:
                return f"Active jusqu'au {self.date_fin}"
            return "Active (en cours)"
        else:
            if self.date_fin and self.date_fin < timezone.now().date():
                return f"Terminée le {self.date_fin}"
            return "À venir"
    
    def save(self, *args, **kwargs):
        """Surcharge save pour mettre à jour le statut utilisateur"""
        super().save(*args, **kwargs)
        # Mettre à jour le statut actif de l'utilisateur associé
        if hasattr(self.sage_femme, 'user') and self.sage_femme.user:
            self.sage_femme.user.update_active_status()
            self.sage_femme.user.save(update_fields=['is_active'])
    
    def delete(self, *args, **kwargs):
        """Surcharge delete pour mettre à jour le statut utilisateur"""
        sage_femme = self.sage_femme
        super().delete(*args, **kwargs)
        # Mettre à jour le statut actif de l'utilisateur associé
        if hasattr(sage_femme, 'user') and sage_femme.user:
            sage_femme.user.update_active_status()
            sage_femme.user.save(update_fields=['is_active'])