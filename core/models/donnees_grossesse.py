"""
Modèle pour les données médicales de grossesse
Informations spécifiques au suivi de grossesse d'une patiente
"""

from django.db import models
from django.core.validators import RegexValidator
from .patient import Patient


class DonneesGrossesse(models.Model):
    """
    Données médicales spécifiques au suivi de grossesse
    Un seul enregistrement par patiente (relation OneToOne)
    """
    patient = models.OneToOneField(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='donnees_grossesse',
        limit_choices_to={'type_patient': 'femme'}
    )
    
    # Obstétrique
    gestite_parite = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Gestité/Parité",
        help_text="Ex: G3P2"
    )
    
    facteurs_risque = models.TextField(
        blank=True, 
        verbose_name="Facteurs de risque"
    )
    
    lieu_accouchement = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Lieu d'accouchement prévu"
    )
    
    # Analyses sanguines de base
    gs_rh = models.CharField(
        max_length=10, 
        blank=True, 
        verbose_name="GS Rh",
        help_text="Ex: A+, O-, AB+"
    )
    
    rai = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="RAI",
        help_text="Recherche d'agglutinines irrégulières"
    )
    
    # Dépistages T1
    ht21 = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="HT21",
        help_text="Dépistage trisomie 21"
    )
    
    dpni = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="DPNI",
        help_text="Dépistage prénatal non invasif"
    )
    
    # Sérologies
    toxo = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Toxo",
        help_text="Sérologie toxoplasmose"
    )
    
    rub = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Rub",
        help_text="Sérologie rubéole"
    )
    
    # Analyses métaboliques
    glyc_jeun = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Glyc à jeun",
        help_text="Glycémie à jeun"
    )
    
    hgpo = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="HGPO",
        help_text="Hyperglycémie provoquée par voie orale"
    )
    
    # Hépatite B
    ag_hbs = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Ag HBs",
        help_text="Antigène HBs"
    )
    
    ac_anti_hbs = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Ac anti HBs",
        help_text="Anticorps anti HBs"
    )
    
    # Autres sérologies
    vih = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="VIH"
    )
    
    tpha_vdrl = models.CharField(
        max_length=30, 
        blank=True, 
        verbose_name="TPHA/VDRL",
        help_text="Sérologie syphilis"
    )
    
    # Numération
    hb = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Hb",
        help_text="Hémoglobine"
    )
    
    plaq = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Plaq",
        help_text="Plaquettes"
    )
    
    # Analyses urinaires/vaginales
    pv = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="PV",
        help_text="Prélèvement vaginal"
    )
    
    ecbu = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="ECBU",
        help_text="Examen cytobactériologique des urines"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Données de grossesse"
        verbose_name_plural = "Données de grossesse"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Données grossesse - {self.patient.nom_complet}"
    
    @property
    def has_data(self):
        """Vérifie si au moins un champ contient des données"""
        fields_to_check = [
            'gestite_parite', 'facteurs_risque', 'lieu_accouchement',
            'gs_rh', 'rai', 'ht21', 'dpni', 'toxo', 'rub', 'glyc_jeun',
            'ag_hbs', 'ac_anti_hbs', 'hgpo', 'vih', 'tpha_vdrl',
            'hb', 'plaq', 'pv', 'ecbu'
        ]
        
        for field in fields_to_check:
            if getattr(self, field, '').strip():
                return True
        return False