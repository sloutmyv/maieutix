from django.db import models
from django.core.exceptions import ValidationError


class SageFemme(models.Model):
    SITUATION_CHOICES = [
        ('gerant', 'Gérant'),
        ('collaborateur', 'Collaborateur'), 
        ('remplacant', 'Remplaçant'),
    ]
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    titre = models.CharField(max_length=100, verbose_name="Titre")
    
    # Contact
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Mail")
    
    # Adresse (optionnelle)
    rue = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rue")
    code_postal = models.CharField(max_length=10, blank=True, null=True, verbose_name="Code postal")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    
    # Informations professionnelles
    numero_cafat = models.CharField(max_length=50, verbose_name="Numéro CAFAT")
    ridet = models.CharField(max_length=50, verbose_name="RIDET")
    rib = models.CharField(max_length=100, verbose_name="RIB")
    banque = models.CharField(max_length=100, verbose_name="Banque")
    
    # Situation professionnelle
    situation = models.CharField(
        max_length=20,
        choices=SITUATION_CHOICES,
        verbose_name="Situation"
    )
    
    # Champs spécifiques aux remplaçants
    remplacement_de = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={'situation__in': ['gerant', 'collaborateur']},
        verbose_name="Remplacement de",
        help_text="Sage-femme remplacée (seulement pour les remplaçants)"
    )
    etat_recapitulatif_commun = models.BooleanField(
        default=False,
        verbose_name="État récapitulatif commun avec le titulaire",
        help_text="Cocher si l'état récapitulatif est commun avec le titulaire"
    )
    bons_depot_communs = models.BooleanField(
        default=False,
        verbose_name="Bons de dépôt communs avec le titulaire",
        help_text="Cocher si les bons de dépôt sont communs avec le titulaire"
    )
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "2. Sage-femme"
        verbose_name_plural = "2. Sages-femmes"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.get_situation_display()})"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Validation pour les remplaçants
        if self.situation == 'remplacant':
            if not self.remplacement_de:
                raise ValidationError({
                    'remplacement_de': 'Un remplaçant doit indiquer qui il remplace.'
                })
            
            # Un remplaçant ne peut pas remplacer un autre remplaçant
            if self.remplacement_de and self.remplacement_de.situation == 'remplacant':
                raise ValidationError({
                    'remplacement_de': 'Un remplaçant ne peut pas remplacer un autre remplaçant.'
                })
        
        # Si ce n'est pas un remplaçant, les champs spécifiques doivent être vides/false
        elif self.situation in ['gerant', 'collaborateur']:
            if self.remplacement_de:
                raise ValidationError({
                    'remplacement_de': 'Seuls les remplaçants peuvent avoir ce champ renseigné.'
                })
    
    def save(self, *args, **kwargs):
        # Réinitialiser les champs spécifiques aux remplaçants si ce n'est pas un remplaçant
        if self.situation != 'remplacant':
            self.remplacement_de = None
            self.etat_recapitulatif_commun = False
            self.bons_depot_communs = False
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def nom_complet(self):
        """Retourne le nom complet"""
        return f"{self.prenom} {self.nom}"
    
    @property
    def adresse_complete(self):
        """Retourne l'adresse complète si disponible"""
        if self.rue and self.code_postal and self.ville:
            return f"{self.rue}, {self.code_postal} {self.ville}"
        return "Adresse non renseignée"