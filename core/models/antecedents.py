from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from .patient import Patient


class Antecedents(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='antecedents',
        verbose_name="Patient"
    )
    
    # Données biométriques
    taille = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.5), MaxValueValidator(2.5)],
        verbose_name="Taille (m)",
        help_text="Taille en mètres"
    )
    poids = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(20), MaxValueValidator(200)],
        verbose_name="Poids (kg)",
        help_text="Poids en kilogrammes"
    )
    
    # Médecins
    medecin_traitant = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Médecin traitant"
    )
    gynecologue = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Gynécologue"
    )
    
    # ATCD médicaux
    allergie = models.TextField(
        blank=True,
        null=True,
        verbose_name="Allergies",
        help_text="Détail des allergies connues"
    )
    asthme = models.BooleanField(
        default=False,
        verbose_name="Asthme"
    )
    raa = models.BooleanField(
        default=False,
        verbose_name="RAA (Rhumatisme articulaire aigu)"
    )
    diabete = models.BooleanField(
        default=False,
        verbose_name="Diabète"
    )
    hta = models.BooleanField(
        default=False,
        verbose_name="HTA (Hypertension artérielle)"
    )
    epilepsie = models.BooleanField(
        default=False,
        verbose_name="Épilepsie"
    )
    infection_urinaire = models.BooleanField(
        default=False,
        verbose_name="Infections urinaires récidivantes"
    )
    atcd_medicaux_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes complémentaires sur les antécédents médicaux"
    )
    
    # ATCD obstétricaux
    atcd_obstetricaux = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antécédents obstétricaux",
        help_text="Grossesses précédentes, accouchements, complications..."
    )
    
    # FCV - Frottis cervico-vaginaux
    fcv_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes FCV",
        help_text="Notes générales sur le suivi FCV"
    )
    
    # ATCD familiaux
    atcd_fam_diabete = models.BooleanField(
        default=False,
        verbose_name="Diabète familial"
    )
    atcd_fam_hta = models.BooleanField(
        default=False,
        verbose_name="HTA familiale"
    )
    atcd_fam_cancer_sein = models.BooleanField(
        default=False,
        verbose_name="Cancer du sein familial"
    )
    atcd_fam_hypercholesterolemie = models.BooleanField(
        default=False,
        verbose_name="Hypercholestérolémie familiale"
    )
    atcd_fam_autre = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes/Autres antécédents"
    )
    
    # ATCD chirurgicaux
    atcd_chirurgicaux = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antécédents chirurgicaux",
        help_text="Interventions chirurgicales antérieures"
    )
    
    # Contraception
    contraception = models.TextField(
        blank=True,
        null=True,
        verbose_name="Contraception",
        help_text="Méthodes contraceptives actuelles et passées"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "6.1.1 Antécédents"
        verbose_name_plural = "6.1.1 Antécédents"
    
    def __str__(self):
        return f"Antécédents de {self.patient.nom_complet}"
    
    @property
    def imc(self):
        """Calcule l'IMC si taille et poids sont renseignés"""
        if self.taille and self.poids:
            return round(self.poids / (self.taille ** 2), 1)
        return None
    
    @property
    def imc_interpretation(self):
        """Interprétation de l'IMC"""
        imc = self.imc
        if not imc:
            return None
        
        if imc < 18.5:
            return "Insuffisance pondérale"
        elif imc < 25:
            return "Poids normal"
        elif imc < 30:
            return "Surpoids"
        elif imc < 35:
            return "Obésité modérée"
        elif imc < 40:
            return "Obésité sévère"
        else:
            return "Obésité morbide"


class FrottisCV(models.Model):
    antecedents = models.ForeignKey(
        Antecedents,
        on_delete=models.CASCADE,
        related_name='frottis',
        verbose_name="Antécédents"
    )
    date_frottis = models.DateField(
        verbose_name="Date du frottis"
    )
    resultat = models.CharField(
        max_length=500,
        verbose_name="Résultat",
        help_text="Résultat du frottis cervico-vaginal"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "6.1.1.1 Frottis cervico-vaginal"
        verbose_name_plural = "6.1.1.1 Frottis cervico-vaginaux"
        ordering = ['-date_frottis']
    
    def __str__(self):
        return f"Frottis du {self.date_frottis.strftime('%d/%m/%Y')} - {self.antecedents.patient.nom_complet}"