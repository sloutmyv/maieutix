"""
Modèle User personnalisé pour les sages-femmes
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class SageFemmeUserManager(BaseUserManager):
    """Gestionnaire personnalisé pour les utilisateurs sages-femmes"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur avec email et mot de passe"""
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un superutilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('must_change_password', False)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class SageFemmeUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle d'utilisateur personnalisé pour les sages-femmes.
    Utilise l'email comme identifiant unique au lieu du nom d'utilisateur.
    """
    
    email = models.EmailField(
        verbose_name="Email",
        unique=True,
        help_text="Adresse email utilisée pour la connexion"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si cet utilisateur peut se connecter"
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff",
        help_text="Indique si l'utilisateur peut accéder à l'administration"
    )
    
    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Doit changer le mot de passe",
        help_text="Indique si l'utilisateur doit changer son mot de passe à la prochaine connexion"
    )
    
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )
    
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier changement de mot de passe"
    )
    
    # Configuration du gestionnaire et champs
    objects = SageFemmeUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "1. Utilisateur Sage-femme"
        verbose_name_plural = "1. Utilisateurs Sages-femmes"
        db_table = 'core_sagefemme_user'
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """Personnalisation de la sauvegarde"""
        # Lors du changement de mot de passe, mettre à jour la date
        if self.pk:
            try:
                old_user = SageFemmeUser.objects.get(pk=self.pk)
                if old_user.password != self.password:
                    self.last_password_change = timezone.now()
                    self.must_change_password = False
            except SageFemmeUser.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def set_default_password(self):
        """Définit le mot de passe par défaut 'azerty'"""
        self.set_password('azerty')
        self.must_change_password = True
        self.last_password_change = None
    
    @property
    def needs_password_change(self):
        """Vérifie si l'utilisateur doit changer son mot de passe"""
        return self.must_change_password