from django.db import models
from django.core.exceptions import ValidationError

class Cabinet(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre")
    rue = models.CharField(max_length=255, verbose_name="Rue")
    code_postal = models.CharField(max_length=10, verbose_name="Code postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Mail")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "1. Cabinet"
        verbose_name_plural = "1. Cabinet"
        ordering = ['titre']
    
    def save(self, *args, **kwargs):
        # Singleton pattern: only one Cabinet allowed
        if not self.pk and Cabinet.objects.exists():
            raise ValidationError("Il ne peut y avoir qu'un seul cabinet.")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion if it's the only cabinet
        raise ValidationError("Le cabinet ne peut pas être supprimé.")
    
    @classmethod
    def get_instance(cls):
        """Get the single Cabinet instance or create it if it doesn't exist"""
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls.objects.create(
                titre="Mon Cabinet",
                rue="",
                code_postal="",
                ville="",
                telephone="",
                email=""
            )
    
    def __str__(self):
        return self.titre