#!/usr/bin/env python
"""
Test final du système d'emails ECOBANK
Envoie un email de test à votre vraie adresse
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def test_final_email():
    """Test final avec votre vraie adresse email"""
    print("📧 TEST FINAL EMAIL ECOBANK")
    print("=" * 50)
    
    # Votre adresse email (remplacez par votre vraie adresse)
    your_email = "votre_email@example.com"  # CHANGEZ CETTE ADRESSE
    
    print(f"📧 Envoi d'un email de test à: {your_email}")
    print("⚠️  IMPORTANT: Changez 'your_email@example.com' par votre vraie adresse dans le script")
    
    try:
        # Test 1: Email simple
        print("\n📧 Test 1: Email simple")
        result = send_mail(
            '🏦 Test ECOBANK - Email Simple',
            'Ceci est un test d\'envoi d\'email simple depuis ECOBANK.',
            settings.DEFAULT_FROM_EMAIL,
            [your_email],
            fail_silently=False
        )
        print(f"✅ Email simple envoyé: {result}")
        
        # Test 2: Email HTML avec template
        print("\n📧 Test 2: Email HTML avec template")
        
        context = {
            'user': {'username': 'Test User'},
            'profile': {'prenom': 'Jean', 'nom': 'Dupont'},
            'date_inscription': '24/10/2025 à 16:30',
            'bank_name': 'ECOBANK Côte d\'Ivoire',
            'support_email': 'support@virement.net',
            'phone_support': '+225 05 04 00 12 72',
        }
        
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = render_to_string('emails/welcome_email.txt', context)
        
        msg = EmailMultiAlternatives(
            '🏦 Test ECOBANK - Email HTML',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [your_email]
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        
        print(f"✅ Email HTML envoyé: {result}")
        
        print("\n" + "=" * 50)
        print("🎉 TESTS TERMINÉS")
        print("📧 Vérifiez votre boîte email (et les spams)")
        print("📧 Si vous ne recevez pas les emails:")
        print("   1. Vérifiez votre boîte spam")
        print("   2. Vérifiez que l'adresse email est correcte")
        print("   3. Vérifiez la configuration SMTP")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_email()
