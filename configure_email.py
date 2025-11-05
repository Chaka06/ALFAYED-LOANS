#!/usr/bin/env python
"""
Script de configuration des emails ECOBANK
Configure les paramètres email et teste la connexion
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def configure_email():
    """Configure et teste le système d'emails"""
    print("🔧 CONFIGURATION DU SYSTÈME D'EMAILS ECOBANK")
    print("=" * 60)
    
    # Afficher la configuration actuelle
    print("\n📋 Configuration actuelle :")
    print(f"   Host SMTP: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   Utilisateur: {settings.EMAIL_HOST_USER}")
    print(f"   Email par défaut: {settings.DEFAULT_FROM_EMAIL}")
    
    # Demander le mot de passe email
    print("\n🔐 Configuration du mot de passe email :")
    print("   Le mot de passe sera stocké dans la variable d'environnement EMAIL_PASSWORD")
    print("   Pour définir le mot de passe, exécutez :")
    print("   export EMAIL_PASSWORD='votre_mot_de_passe_email'")
    
    # Test de connexion
    print("\n🧪 Test de connexion SMTP...")
    try:
        # Test simple d'envoi d'email
        send_mail(
            subject='Test ECOBANK - Configuration Email',
            message='Ceci est un email de test pour vérifier la configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print("✅ Connexion SMTP réussie !")
        print("✅ Configuration email validée")
        
    except Exception as e:
        print(f"❌ Erreur de connexion SMTP: {e}")
        print("\n🔧 Solutions possibles :")
        print("   1. Vérifiez que le mot de passe EMAIL_PASSWORD est correct")
        print("   2. Vérifiez les paramètres SMTP dans settings.py")
        print("   3. Vérifiez votre connexion internet")
        print("   4. Contactez votre fournisseur d'email")
    
    print("\n" + "=" * 60)
    print("📧 SYSTÈME D'EMAILS ECOBANK CONFIGURÉ")
    print("=" * 60)

if __name__ == "__main__":
    configure_email()
