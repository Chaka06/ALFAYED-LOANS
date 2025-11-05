#!/usr/bin/env python
"""
Test de débogage du système d'emails ECOBANK
Vérifie si les emails sont vraiment envoyés
"""

import os
import sys
import django
import time
import logging

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User
from loan_system.models import UserProfile, LoanRequest
from loan_system.email_async import FastECOBANKEmailService
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

def test_email_system_debug():
    """Test détaillé du système d'emails"""
    print("🔍 DÉBOGAGE SYSTÈME D'EMAILS ECOBANK")
    print("=" * 60)
    
    # Test 1: Email direct Django
    print("\n📧 Test 1: Email direct Django")
    try:
        result = send_mail(
            'Test ECOBANK Direct',
            'Ceci est un test d\'envoi d\'email direct.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False
        )
        print(f"✅ Email direct envoyé: {result}")
    except Exception as e:
        print(f"❌ Erreur email direct: {e}")
    
    # Test 2: Service asynchrone
    print("\n📧 Test 2: Service asynchrone")
    try:
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_email_debug',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Email'
            }
        )
        
        if created:
            print("✅ Utilisateur de test créé")
        else:
            print("ℹ️ Utilisateur de test existant")
        
        # Créer le profil
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'prenom': 'Jean',
                'nom': 'Dupont',
                'telephone': '+225 07 12 34 56 78',
                'adresse': 'Abidjan, Côte d\'Ivoire',
                'profession': 'Ingénieur',
                'revenus_mensuels': 500000,
                'is_validated': True
            }
        )
        
        print("✅ Profil utilisateur configuré")
        
        # Test email de bienvenue
        print("\n📧 Test email de bienvenue...")
        result = FastECOBANKEmailService.send_welcome_email_fast(user)
        print(f"✅ Email de bienvenue: {result}")
        
        # Attendre un peu pour voir les logs
        print("⏳ Attente de 3 secondes pour voir les logs...")
        time.sleep(3)
        
        # Test notification de connexion
        print("\n📧 Test notification de connexion...")
        result = FastECOBANKEmailService.send_login_alert_fast(user, "192.168.1.100")
        print(f"✅ Notification connexion: {result}")
        
        # Attendre un peu
        time.sleep(3)
        
        # Test alerte changement mot de passe
        print("\n📧 Test alerte changement mot de passe...")
        result = FastECOBANKEmailService.send_password_change_alert_fast(user)
        print(f"✅ Alerte changement mot de passe: {result}")
        
        # Attendre un peu
        time.sleep(3)
        
        print("\n" + "=" * 60)
        print("🎉 TESTS TERMINÉS")
        print("Vérifiez les logs ci-dessus pour voir les erreurs éventuelles")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_system_debug()
