from django.db import models
from django.core.validators import RegexValidator
from .caisse import Caisse


class Patient(models.Model):
    TYPE_CHOICES = [
        ('femme', 'Femme'),
        ('bebe', 'Bébé'),
    ]
    
    type_patient = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='femme',
        verbose_name="Type de patient"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    nom_jf = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nom de jeune fille"
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Profession"
    )
    telephone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^(\+33|0)[1-9](\d{8})$',
            message="Format: 0123456789 ou +33123456789"
        )],
        verbose_name="Téléphone"
    )
    numero_ep = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro EP"
    )
    date_debut_grossesse = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de début de grossesse",
        help_text="Uniquement pour les femmes"
    )
    
    # Relation mère-enfant
    mere = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='bebes',
        verbose_name="Mère",
        help_text="Uniquement pour les bébés"
    )
    
    # Gestion de l'assurance
    est_assure_titulaire = models.BooleanField(
        default=True,
        verbose_name="Assuré principal"
    )
    
    # Informations de l'assuré titulaire (si différent du patient)
    nom_assure = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nom de l'assuré"
    )
    prenom_assure = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Prénom de l'assuré"
    )
    date_naissance_assure = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de naissance de l'assuré"
    )
    
    # Adresse de l'assuré
    rue_assure = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Rue (assuré)"
    )
    code_postal_assure = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{5}$',
            message="Le code postal doit contenir 5 chiffres"
        )],
        verbose_name="Code postal (assuré)"
    )
    commune_assure = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Commune (assuré)"
    )
    
    # Caisse d'assurance
    caisse = models.ForeignKey(
        Caisse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Caisse d'assurance"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Patient actif"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "6. Patient"
        verbose_name_plural = "6. Patients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        if self.type_patient == 'bebe' and self.mere:
            return f"{self.prenom} {self.nom} (bébé de {self.mere.prenom} {self.mere.nom})"
        return f"{self.prenom} {self.nom}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        # Validation des dates
        today = date.today()
        
        if self.date_naissance and self.date_naissance > today:
            raise ValidationError("La date de naissance ne peut pas être dans le futur.")
        
        if self.date_debut_grossesse and self.date_debut_grossesse > today:
            raise ValidationError("La date de début de grossesse ne peut pas être dans le futur.")
        
        if self.date_naissance_assure and self.date_naissance_assure > today:
            raise ValidationError("La date de naissance de l'assuré ne peut pas être dans le futur.")
        
        # Validation des règles métier
        if self.type_patient == 'bebe':
            if not self.mere:
                raise ValidationError("Un bébé doit avoir une mère.")
            if self.mere.type_patient != 'femme':
                raise ValidationError("La mère d'un bébé doit être une femme.")
            if self.date_debut_grossesse:
                raise ValidationError("Un bébé ne peut pas avoir de date de début de grossesse.")
            if self.est_assure_titulaire:
                raise ValidationError("Un bébé ne peut pas être assuré titulaire.")
        
        if self.type_patient == 'femme' and self.mere:
            raise ValidationError("Une femme ne peut pas avoir de mère assignée.")
        
        # Validation de l'assurance
        if not self.est_assure_titulaire:
            if not all([self.nom_assure, self.prenom_assure, self.date_naissance_assure, self.rue_assure, self.code_postal_assure, self.commune_assure]):
                raise ValidationError("Les informations complètes de l'assuré titulaire sont obligatoires.")
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
    
    @property
    def age_detail(self):
        """Retourne l'âge détaillé pour les bébés"""
        from datetime import date
        today = date.today()
        delta = today - self.date_naissance
        
        if self.type_patient == 'bebe':
            jours = delta.days
            
            # Moins d'une semaine : en jours
            if jours < 7:
                if jours == 0:
                    return "Nouveau-né"
                elif jours == 1:
                    return "1 jour"
                else:
                    return f"{jours} jours"
            
            # Moins d'un mois : en semaines
            elif jours < 30:
                semaines = jours // 7
                jours_reste = jours % 7
                if semaines == 1:
                    if jours_reste == 0:
                        return "1 semaine"
                    elif jours_reste == 1:
                        return "1 semaine et 1 jour"
                    else:
                        return f"1 semaine et {jours_reste} jours"
                else:
                    if jours_reste == 0:
                        return f"{semaines} semaines"
                    elif jours_reste == 1:
                        return f"{semaines} semaines et 1 jour"
                    else:
                        return f"{semaines} semaines et {jours_reste} jours"
            
            # Moins d'un an : en mois et jours
            elif jours < 365:
                mois = jours // 30
                jours_reste = jours % 30
                if mois == 1:
                    if jours_reste == 0:
                        return "1 mois"
                    elif jours_reste == 1:
                        return "1 mois et 1 jour"
                    else:
                        return f"1 mois et {jours_reste} jours"
                else:
                    if jours_reste == 0:
                        return f"{mois} mois"
                    elif jours_reste == 1:
                        return f"{mois} mois et 1 jour"
                    else:
                        return f"{mois} mois et {jours_reste} jours"
            
            # Moins de 2 ans : en années et mois
            elif jours < 730:
                annees = jours // 365
                mois = (jours % 365) // 30
                if annees == 1:
                    if mois == 0:
                        return "1 an"
                    elif mois == 1:
                        return "1 an et 1 mois"
                    else:
                        return f"1 an et {mois} mois"
                else:
                    if mois == 0:
                        return f"{annees} ans"
                    elif mois == 1:
                        return f"{annees} ans et 1 mois"
                    else:
                        return f"{annees} ans et {mois} mois"
        
        # Pour les femmes ou bébés de plus de 2 ans
        age = self.age
        if age == 0:
            return "Moins d'1 an"
        elif age == 1:
            return "1 an"
        else:
            return f"{age} ans"
    
    @property
    def date_terme(self):
        """Calcule la date du terme (début de grossesse + 280 jours)"""
        if self.type_patient == 'femme' and self.date_debut_grossesse:
            from datetime import timedelta
            return self.date_debut_grossesse + timedelta(days=280)
        return None
    
    @property
    def age_grossesse(self):
        """Calcule l'âge de la grossesse en semaines et jours"""
        if self.type_patient == 'femme' and self.date_debut_grossesse:
            from datetime import date
            today = date.today()
            delta = today - self.date_debut_grossesse
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
                    return "1 semaine"
                elif jours_reste == 1:
                    return "1 semaine et 1 jour"
                else:
                    return f"1 semaine et {jours_reste} jours"
            else:
                if jours_reste == 0:
                    return f"{semaines} semaines"
                elif jours_reste == 1:
                    return f"{semaines} semaines et 1 jour"
                else:
                    return f"{semaines} semaines et {jours_reste} jours"
        return None
    
    def get_bebes(self):
        """Retourne les bébés de cette femme"""
        if self.type_patient == 'femme':
            return self.bebes.all()
        return Patient.objects.none()
    
    def get_assure_info(self):
        """Retourne les informations de l'assuré (patient lui-même ou titulaire)"""
        if self.est_assure_titulaire:
            return {
                'nom': self.nom,
                'prenom': self.prenom,
                'date_naissance': self.date_naissance,
                'adresse': None
            }
        else:
            return {
                'nom': self.nom_assure,
                'prenom': self.prenom_assure,
                'date_naissance': self.date_naissance_assure,
                'adresse': {
                    'rue': self.rue_assure,
                    'code_postal': self.code_postal_assure,
                    'commune': self.commune_assure
                }
            }