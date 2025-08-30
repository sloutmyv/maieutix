from django.db import models


class CadreExercice(models.Model):
    """
    Modèle représentant un cadre d'exercice pour les sages-femmes
    """
    
    # Label du cadre d'exercice
    label = models.CharField(
        max_length=200,
        verbose_name="Label",
        help_text="Nom du cadre d'exercice"
    )
    
    # Description détaillée
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée du cadre d'exercice"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "4.1 Cadre d'exercice"
        verbose_name_plural = "4.1 Cadres d'exercice"
        ordering = ['label']
    
    def __str__(self):
        return self.label