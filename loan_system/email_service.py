"""
Service d'envoi d'emails automatiques pour Investor Banque
Gère tous les emails professionnels aux grandes étapes bancaires
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile, LoanRequest, Payment
import logging

logger = logging.getLogger(__name__)

class ECOBANKEmailService:
    """Service d'envoi d'emails professionnels Investor Banque"""
    
    @staticmethod
    def send_welcome_email(user):
        """Email de bienvenue après inscription"""
        try:
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'date_inscription': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
            }
            
            subject = f"Bienvenue chez Investor Banque - Compte créé avec succès"
            html_content = render_to_string('emails/welcome_email.html', context)
            text_content = render_to_string('emails/welcome_email.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email de bienvenue envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email bienvenue: {e}")
            return False
    
    @staticmethod
    def send_login_notification(user, ip_address=None):
        """Notification de connexion"""
        try:
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'login_time': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'ip_address': ip_address or 'Non disponible',
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
            }
            
            subject = f"Connexion à votre compte Investor Banque"
            html_content = render_to_string('emails/login_alert.html', context)
            text_content = render_to_string('emails/login_alert.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Notification de connexion envoyée à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi notification connexion: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_link):
        """Email de réinitialisation de mot de passe"""
        try:
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'reset_link': reset_link,
                'expiry_time': '24 heures',
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Réinitialisation de votre mot de passe Investor Banque"
            html_content = render_to_string('emails/password_reset.html', context)
            text_content = render_to_string('emails/password_reset.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email de réinitialisation envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email réinitialisation: {e}")
            return False
    
    @staticmethod
    def send_password_change_alert(user):
        """Alerte de changement de mot de passe"""
        try:
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'change_time': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Modification de votre mot de passe Investor Banque"
            html_content = render_to_string('emails/password_change_alert.html', context)
            text_content = render_to_string('emails/password_change_alert.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Alerte changement mot de passe envoyée à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi alerte changement mot de passe: {e}")
            return False
    
    @staticmethod
    def send_loan_request_confirmation(loan_request):
        """Confirmation de demande de prêt"""
        try:
            user = loan_request.user
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'request_date': loan_request.date_demande.strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Confirmation de votre demande de prêt INV-{loan_request.id:06d}"
            html_content = render_to_string('emails/loan_request_confirmation.html', context)
            text_content = render_to_string('emails/loan_request_confirmation.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Confirmation demande prêt envoyée à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi confirmation demande prêt: {e}")
            return False
    
    @staticmethod
    def send_loan_approval_email(loan_request):
        """Email d'approbation de prêt"""
        try:
            user = loan_request.user
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'approval_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Félicitations ! Votre prêt INV-{loan_request.id:06d} a été approuvé"
            html_content = render_to_string('emails/loan_approval.html', context)
            text_content = render_to_string('emails/loan_approval.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email d'approbation envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email approbation: {e}")
            return False
    
    @staticmethod
    def send_payment_instructions_email(loan_request, payment):
        """Instructions de paiement de l'avance"""
        try:
            user = loan_request.user
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'payment': payment,
                'payment_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Instructions de paiement - Prêt INV-{loan_request.id:06d}"
            html_content = render_to_string('emails/payment_instructions.html', context)
            text_content = render_to_string('emails/payment_instructions.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Instructions de paiement envoyées à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi instructions paiement: {e}")
            return False
    
    @staticmethod
    def send_subscription_activated_email(user):
        """Email d'activation de compte"""
        try:
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'activation_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
            }
            
            subject = f"Votre compte Investor Banque est maintenant actif"
            html_content = render_to_string('emails/subscription_activated.html', context)
            text_content = render_to_string('emails/subscription_activated.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email d'activation envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email activation: {e}")
            return False
