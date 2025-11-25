from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
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
            MinValueValidator(Decimal('5000.00')),  # 5 000 EUR
            MaxValueValidator(Decimal('5000000.00'))  # 5 000 000 EUR
        ],
        verbose_name="Montant demandé (EUR)"
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
        verbose_name="Montant d'avance (10%)",
        default=Decimal('0.00')
    )
    duree_remboursement_mois = models.IntegerField(
        default=84,
        verbose_name="Durée de remboursement (mois)"
    )  # 12 mois à 300 mois (25 ans) max
    
    class Meta:
        verbose_name = "Demande de prêt"
        verbose_name_plural = "Demandes de prêts"
        ordering = ['-date_demande']
    
    def save(self, *args, **kwargs):
        # Calculer le montant d'avance (10%) - Utiliser Decimal au lieu de float
        if self.montant:
            self.montant_avance = self.montant * Decimal('0.10')
        
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
        return f"Demande de {self.user.username} - {self.montant:,.0f} EUR"

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

class Message(models.Model):
    """Système de messagerie interne entre clients et gestionnaire"""
    STATUS_CHOICES = [
        ('non_lu', 'Non lu'),
        ('lu', 'Lu'),
        ('repondu', 'Répondu'),
    ]
    
    PRIORITY_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    # Participants
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Expéditeur"
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="Destinataire"
    )
    
    # Contenu du message
    subject = models.CharField(
        max_length=200, 
        verbose_name="Sujet"
    )
    content = models.TextField(
        verbose_name="Contenu du message"
    )
    
    # Métadonnées
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='non_lu',
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normale',
        verbose_name="Priorité"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date d'envoi"
    )
    read_at = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Date de lecture"
    )
    
    # Réponse (si c'est une réponse à un message)
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='replies',
        verbose_name="Message parent"
    )
    
    # Lien avec une demande de prêt (optionnel)
    loan_request = models.ForeignKey(
        LoanRequest, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        verbose_name="Demande de prêt liée"
    )
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message de {self.sender.username} à {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        if self.status == 'non_lu':
            self.status = 'lu'
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_replied(self):
        """Marquer le message comme répondu"""
        self.status = 'repondu'
        self.save()
    
    @property
    def is_from_client(self):
        """Vérifier si le message vient d'un client"""
        return not self.sender.is_staff
    
    @property
    def is_from_manager(self):
        """Vérifier si le message vient du gestionnaire"""
        return self.sender.is_staff
    
    @property
    def time_since_created(self):
        """Temps écoulé depuis la création"""
        if not self.created_at:
            return "Date inconnue"
            
        now = timezone.now()
        delta = now - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} jour(s) ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} heure(s) ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute(s) ago"
        else:
            return "À l'instant"

class Notification(models.Model):
    """Système de notifications pour les utilisateurs"""
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('non_lu', 'Non lu'),
        ('lu', 'Lu'),
        ('archive', 'Archivé'),
    ]
    
    # Contenu
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    notification_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='info',
        verbose_name="Type"
    )
    
    # Destinataire
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="Destinataire"
    )
    
    # Expéditeur (admin)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications',
        verbose_name="Expéditeur"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='non_lu',
        verbose_name="Statut"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de lecture")
    
    # Lien optionnel
    action_url = models.URLField(blank=True, null=True, verbose_name="Lien d'action")
    action_text = models.CharField(max_length=100, blank=True, null=True, verbose_name="Texte du lien")
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification pour {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if self.status == 'non_lu':
            self.status = 'lu'
            self.read_at = timezone.now()
            self.save()
    
    def archive(self):
        """Archiver la notification"""
        self.status = 'archive'
        self.save()
    
    @property
    def is_unread(self):
        """Vérifier si la notification est non lue"""
        return self.status == 'non_lu'
    
    @property
    def time_since_created(self):
        """Temps écoulé depuis la création"""
        if not self.created_at:
            return "Date inconnue"
            
        now = timezone.now()
        delta = now - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} jour(s) ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} heure(s) ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute(s) ago"
        else:
            return "À l'instant"