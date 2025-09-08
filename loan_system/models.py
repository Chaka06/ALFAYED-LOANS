from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
import secrets
import string
from datetime import date, timedelta

class UserProfile(models.Model):
    MARITAL_STATUS_CHOICES = [
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, verbose_name="Nom", blank=True)
    prenom = models.CharField(max_length=100, verbose_name="Prénom", blank=True)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    lieu_naissance = models.CharField(max_length=200, verbose_name="Lieu de naissance", blank=True)
    situation_matrimoniale = models.CharField(
        max_length=20, 
        choices=MARITAL_STATUS_CHOICES,
        verbose_name="Situation matrimoniale",
        blank=True
    )
    profession = models.CharField(max_length=200, verbose_name="Profession", blank=True)
    adresse = models.TextField(verbose_name="Adresse", blank=True)
    
    # Documents
    piece_identite_recto = models.ImageField(
        upload_to='documents/identite/',
        verbose_name="Pièce d'identité (recto)",
        null=True,
        blank=True
    )
    piece_identite_verso = models.ImageField(
        upload_to='documents/identite/',
        verbose_name="Pièce d'identité (verso)",
        null=True,
        blank=True
    )
    justificatif_adresse = models.FileField(
        upload_to='documents/justificatifs/',
        verbose_name="Justificatif d'adresse",
        null=True,
        blank=True
    )
    autre_document = models.FileField(
        upload_to='documents/autres/', 
        blank=True, 
        null=True,
        verbose_name="Autre document (optionnel)"
    )
    
    # Statut de validation
    is_validated = models.BooleanField(default=False, verbose_name="Compte validé")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_validation = models.DateTimeField(blank=True, null=True, verbose_name="Date de validation")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        if self.nom and self.prenom:
            return f"{self.nom} {self.prenom}"
        return f"Profil de {self.user.username}"
    
    def is_complete(self):
        """Vérifie si le profil est complet"""
        required_fields = [
            self.nom, self.prenom, self.date_naissance, self.lieu_naissance,
            self.situation_matrimoniale, self.profession, self.adresse,
            self.piece_identite_recto, self.piece_identite_verso, self.justificatif_adresse
        ]
        return all(field for field in required_fields)

# Signal pour créer automatiquement un profil utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

class LoanRequest(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('paye', 'Payé'),
        ('active', 'Actif'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    montant = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('5000000.00')),  # 5 millions
            MaxValueValidator(Decimal('50000000.00'))  # 50 millions
        ],
        verbose_name="Montant demandé (FCFA)"
    )
    motif = models.TextField(verbose_name="Motif de la demande")
    document_projet = models.FileField(
        upload_to='documents/projets/',
        verbose_name="Document détaillant le projet"
    )
    
    # Statut et dates
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='en_attente',
        verbose_name="Statut"
    )
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    date_validation = models.DateTimeField(blank=True, null=True, verbose_name="Date de validation")
    date_paiement = models.DateTimeField(blank=True, null=True, verbose_name="Date de paiement")
    
    # Clé de paiement
    payment_key = models.CharField(
        max_length=12, 
        blank=True,
        verbose_name="Clé de paiement"
    )
    
    # Informations de remboursement
    montant_avance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        editable=False,
        verbose_name="Montant d'avance (15%)",
        default=Decimal('0.00')
    )
    duree_remboursement_mois = models.IntegerField(
        default=84,
        verbose_name="Durée de remboursement (mois)"
    )  # 7 ans max
    
    class Meta:
        verbose_name = "Demande de prêt"
        verbose_name_plural = "Demandes de prêts"
        ordering = ['-date_demande']
    
    def save(self, *args, **kwargs):
        # Calculer le montant d'avance (15%) - Utiliser Decimal au lieu de float
        if self.montant:
            self.montant_avance = self.montant * Decimal('0.15')
        
        # Générer la clé de paiement si le statut est validé
        if self.status == 'valide' and not self.payment_key:
            self.payment_key = self.generate_payment_key()
            
        super().save(*args, **kwargs)
    
    def generate_payment_key(self):
        """Génère une clé de paiement de 12 caractères"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(12))
    
    @property
    def date_fin_remboursement(self):
        if self.date_paiement:
            return self.date_paiement.date() + timedelta(days=self.duree_remboursement_mois * 30)
        return None
    
    def __str__(self):
        return f"Demande de {self.user.username} - {self.montant:,.0f} FCFA"

class Payment(models.Model):
    loan_request = models.OneToOneField(
        LoanRequest, 
        on_delete=models.CASCADE,
        verbose_name="Demande de prêt"
    )
    payment_key_entered = models.CharField(
        max_length=12,
        verbose_name="Clé de paiement saisie"
    )
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='validated_payments',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de validation"
    )
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
    
    def __str__(self):
        return f"Paiement pour {self.loan_request}"