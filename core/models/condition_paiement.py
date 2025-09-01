from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ConditionPaiement(models.Model):
    designation = models.CharField(max_length=200, verbose_name="Désignation")
    pourcentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage à payer (%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "5.1 Condition de paiement"
        verbose_name_plural = "5.1 Conditions de paiement"
        ordering = ['designation']

    def __str__(self):
        return f"{self.designation} ({self.pourcentage}%)"