from django.db import models
from .condition_paiement import ConditionPaiement


class Caisse(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom de la caisse")
    conditions_paiement_eligibles = models.ManyToManyField(
        ConditionPaiement,
        blank=True,
        related_name='caisses_eligibles',
        verbose_name="Conditions de paiement éligibles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "5. Caisse"
        verbose_name_plural = "5. Caisses"
        ordering = ['nom']

    def __str__(self):
        return self.nom
    
    def get_conditions_eligibles(self):
        return self.conditions_paiement_eligibles.all()
    
    def is_eligible_for_condition(self, condition_paiement):
        return self.conditions_paiement_eligibles.filter(id=condition_paiement.id).exists()