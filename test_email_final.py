#!/usr/bin/env python
"""
Test final du système d'emails ECOBANK avec le bon mot de passe
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_connection():
    """Test de connexion email avec le bon mot de passe"""
    print("🧪 TEST DE CONNEXION EMAIL ECOBANK")
    print("=" * 50)
    
    # Afficher la configuration
    print(f"📧 Host SMTP: {settings.EMAIL_HOST}")
    print(f"📧 Port: {settings.EMAIL_PORT}")
    print(f"📧 TLS: {settings.EMAIL_USE_TLS}")
    print(f"📧 Utilisateur: {settings.EMAIL_HOST_USER}")
    print(f"📧 Mot de passe: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
    
    # Test d'envoi d'email simple
    print("\n🚀 Test d'envoi d'email...")
    try:
        send_mail(
            subject='Test ECOBANK - Configuration Email',
            message='Ceci est un email de test pour vérifier la configuration du système ECOBANK.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Email de test
            fail_silently=False,
        )
        print("✅ Email envoyé avec succès !")
        print("✅ Configuration email validée")
        
    except Exception as e:
        print(f"❌ Erreur d'envoi: {e}")
        print("\n🔧 Solutions possibles :")
        print("   1. Vérifiez que le mot de passe est correct")
        print("   2. Vérifiez la connexion internet")
        print("   3. Vérifiez les paramètres SMTP")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_email_connection()
