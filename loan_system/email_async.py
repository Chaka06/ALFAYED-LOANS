"""
Service d'envoi d'emails asynchrone pour Investor Banque
Optimisé pour la vitesse et la fiabilité
"""

import threading
import time
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile, LoanRequest, Payment, Notification, Message
import logging

logger = logging.getLogger(__name__)

class FastInvestorEmailService:
    """Service d'envoi d'emails rapide et asynchrone pour Investor Banque"""
    
    @staticmethod
    def send_email_async(subject, html_content, text_content, recipient_email, from_email=None):
        """Envoi asynchrone d'email pour la vitesse"""
        def send_email_thread():
            try:
                email_from = from_email if from_email else settings.DEFAULT_FROM_EMAIL
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=email_from,
                    to=[recipient_email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
                logger.info(f"Email envoyé avec succès à {recipient_email}")
            except Exception as e:
                logger.error(f"Erreur envoi email à {recipient_email}: {e}")
        
        # Lancer l'envoi dans un thread séparé pour la vitesse
        thread = threading.Thread(target=send_email_thread)
        thread.daemon = True
        thread.start()
        return True
    
    @staticmethod
    def send_welcome_email_fast(user):
        """Email de bienvenue rapide"""
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
            
            subject = f"🏦 Bienvenue chez Investor Banque - Compte créé avec succès"
            html_content = render_to_string('emails/welcome_email.html', context)
            text_content = render_to_string('emails/welcome_email.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email bienvenue: {e}")
            return False
    
    @staticmethod
    def send_login_alert_fast(user, ip_address=None):
        """Notification de connexion rapide"""
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
            
            subject = f"🔐 Connexion à votre compte Investor Banque"
            html_content = render_to_string('emails/login_alert.html', context)
            text_content = render_to_string('emails/login_alert.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur notification connexion: {e}")
            return False
    
    @staticmethod
    def send_password_change_alert_fast(user):
        """Alerte changement mot de passe rapide"""
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
            
            subject = f"🔒 Modification de votre mot de passe Investor Banque"
            html_content = render_to_string('emails/password_change_alert.html', context)
            text_content = render_to_string('emails/password_change_alert.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur alerte changement mot de passe: {e}")
            return False
    
    @staticmethod
    def send_loan_request_confirmation_fast(loan_request):
        """Confirmation demande de prêt rapide"""
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
            
            subject = f"📋 Confirmation de votre demande de prêt INV-{loan_request.id:06d}"
            html_content = render_to_string('emails/loan_request_confirmation.html', context)
            text_content = render_to_string('emails/loan_request_confirmation.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur confirmation demande prêt: {e}")
            return False
    
    @staticmethod
    def send_loan_approval_fast(loan_request):
        """Email d'approbation de prêt rapide"""
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
            
            subject = f"🎉 Félicitations ! Votre prêt INV-{loan_request.id:06d} a été approuvé"
            html_content = render_to_string('emails/loan_approval.html', context)
            text_content = render_to_string('emails/loan_approval.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email approbation: {e}")
            return False
    
    @staticmethod
    def send_subscription_activated_fast(user):
        """Email d'activation de compte rapide"""
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
            
            subject = f"✅ Votre compte Investor Banque est maintenant actif"
            html_content = render_to_string('emails/subscription_activated.html', context)
            text_content = render_to_string('emails/subscription_activated.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email activation: {e}")
            return False
    
    @staticmethod
    def send_loan_rejection_fast(loan_request):
        """Email de rejet de prêt rapide"""
        try:
            user = loan_request.user
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'rejection_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
            }
            
            subject = f"❌ Décision concernant votre demande de prêt INV-{loan_request.id:06d}"
            html_content = render_to_string('emails/loan_rejection.html', context)
            text_content = render_to_string('emails/loan_rejection.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email rejet: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation_fast(loan_request, payment):
        """Email de confirmation de paiement rapide"""
        try:
            user = loan_request.user
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'payment': payment,
                'payment_date': payment.date_validation.strftime('%d/%m/%Y à %H:%M') if payment.date_validation else timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
            }
            
            subject = f"✅ Paiement confirmé - Prêt INV-{loan_request.id:06d}"
            html_content = render_to_string('emails/payment_confirmation.html', context)
            text_content = render_to_string('emails/payment_confirmation.txt', context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email confirmation paiement: {e}")
            return False
    
    @staticmethod
    def send_status_change_email_fast(loan_request, old_status, new_status):
        """Email générique pour changement de statut - route vers le bon template selon le statut"""
        status_email_map = {
            'valide': 'loan_approved',
            'rejete': 'loan_rejected',
            'paye': 'loan_paid',
            'active': 'loan_active',
            'en_attente': 'loan_pending',
        }
        
        if new_status not in status_email_map:
            return False
        
        email_type = status_email_map[new_status]
        
        try:
            user = loan_request.user
            profile = user.userprofile
            status_date = timezone.now().strftime('%d/%m/%Y à %H:%M')
            
            context = {
                'user': user,
                'profile': profile,
                'loan_request': loan_request,
                'status_date': status_date,
                'old_status': old_status,
                'new_status': new_status,
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
            }
            
            # Sélection du template et sujet selon le statut
            if new_status == 'valide':
                subject = f"✅ Votre prêt INV-{loan_request.id:06d} a été validé"
                html_template = 'emails/loan_status_validated.html'
                txt_template = 'emails/loan_status_validated.txt'
            elif new_status == 'rejete':
                subject = f"❌ Décision concernant votre demande de prêt INV-{loan_request.id:06d}"
                html_template = 'emails/loan_rejection.html'
                txt_template = 'emails/loan_rejection.txt'
            elif new_status == 'paye':
                subject = f"✅ Paiement confirmé - Prêt INV-{loan_request.id:06d}"
                html_template = 'emails/loan_status_paid.html'
                txt_template = 'emails/loan_status_paid.txt'
            elif new_status == 'active':
                subject = f"🎉 Votre prêt INV-{loan_request.id:06d} est maintenant actif"
                html_template = 'emails/loan_status_active.html'
                txt_template = 'emails/loan_status_active.txt'
            elif new_status == 'en_attente':
                subject = f"📋 Votre demande de prêt INV-{loan_request.id:06d} est en attente"
                html_template = 'emails/loan_status_pending.html'
                txt_template = 'emails/loan_status_pending.txt'
            else:
                return False
            
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(txt_template, context)
            
            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
            
        except Exception as e:
            logger.error(f"Erreur email changement statut {new_status}: {e}")
            return False

    @staticmethod
    def send_notification_email_fast(notification: Notification):
        """Envoi d'un email lors de la création d'une Notification pour un client"""
        try:
            user = notification.recipient
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'notification': notification,
                'title': notification.title,
                'content': notification.content,
                'created_at': notification.created_at.strftime('%d/%m/%Y à %H:%M') if notification.created_at else timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'action_url': notification.action_url,
                'action_text': notification.action_text,
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
            }

            subject = f"🔔 Notification: {notification.title}"
            html_content = render_to_string('emails/notification.html', context)
            text_content = render_to_string('emails/notification.txt', context)

            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
        except Exception as e:
            logger.error(f"Erreur email notification: {e}")
            return False

    @staticmethod
    def send_message_email_fast(message: Message):
        """Envoi d'un email au client quand un message est envoyé par l'admin"""
        try:
            # N'envoyer l'email que si l'expéditeur est staff (gestionnaire) et le destinataire est un client
            if not message.sender.is_staff or message.recipient.is_staff:
                return False

            user = message.recipient
            profile = user.userprofile
            context = {
                'user': user,
                'profile': profile,
                'message': message,
                'subject': message.subject,
                'content': message.content,
                'created_at': message.created_at.strftime('%d/%m/%Y à %H:%M') if message.created_at else timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'loan_request': message.loan_request,
                'bank_name': 'Investor Banque',
                'manager_name': 'Damien Boudraux',
                'manager_email': 'damien.boudraux17@outlook.fr',
                'support_email': 'support@virement.net',
                'phone_support': '+49 157 50098219',
            }

            subject = f"📩 Nouveau message de votre gestionnaire: {message.subject}"
            html_content = render_to_string('emails/new_message.html', context)
            text_content = render_to_string('emails/new_message.txt', context)

            return FastInvestorEmailService.send_email_async(
                subject, html_content, text_content, user.email
            )
        except Exception as e:
            logger.error(f"Erreur email message: {e}")
            return False
