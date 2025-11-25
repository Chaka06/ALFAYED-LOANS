#!/usr/bin/env python
"""
Test complet du système d'emails ECOBANK
Simule tous les scénarios d'envoi d'emails
"""

import os
import sys
import django
import time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.contrib.auth.models import User
from loan_system.models import UserProfile, LoanRequest
from loan_system.email_async import FastECOBANKEmailService
from decimal import Decimal

def test_complete_email_system():
    """Test complet du système d'emails"""
    print("🚀 TEST COMPLET SYSTÈME D'EMAILS ECOBANK")
    print("=" * 60)
    
    # Créer un utilisateur de test
    try:
        user, created = User.objects.get_or_create(
            username='test_complete_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Complete'
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
                'is_validated': False  # Pas encore validé
            }
        )
        
        print("✅ Profil utilisateur configuré")
        
        # Test 1: Email de bienvenue (inscription)
        print("\n📧 Test 1: Email de bienvenue (inscription)")
        try:
            result = FastECOBANKEmailService.send_welcome_email_fast(user)
            print(f"✅ Email de bienvenue envoyé: {result}")
        except Exception as e:
            print(f"❌ Erreur email de bienvenue: {e}")
        
        time.sleep(2)
        
        # Test 2: Notification de connexion
        print("\n📧 Test 2: Notification de connexion")
        try:
            result = FastECOBANKEmailService.send_login_alert_fast(user, "192.168.1.100")
            print(f"✅ Notification connexion envoyée: {result}")
        except Exception as e:
            print(f"❌ Erreur notification connexion: {e}")
        
        time.sleep(2)
        
        # Test 3: Alerte changement mot de passe
        print("\n📧 Test 3: Alerte changement mot de passe")
        try:
            result = FastECOBANKEmailService.send_password_change_alert_fast(user)
            print(f"✅ Alerte changement mot de passe envoyée: {result}")
        except Exception as e:
            print(f"❌ Erreur alerte changement mot de passe: {e}")
        
        time.sleep(2)
        
        # Test 4: Créer une demande de prêt
        print("\n📧 Test 4: Confirmation de demande de prêt")
        try:
            loan_request, created = LoanRequest.objects.get_or_create(
                user=user,
                defaults={
                    'montant': Decimal('10000000'),  # 10 millions
                    'motif': 'Test système emails complet',
                    'document_projet': None,
                    'status': 'en_attente',
                    'duree_remboursement_mois': 12
                }
            )
            
            if created:
                print("✅ Demande de prêt créée")
            
            result = FastECOBANKEmailService.send_loan_request_confirmation_fast(loan_request)
            print(f"✅ Confirmation demande de prêt envoyée: {result}")
        except Exception as e:
            print(f"❌ Erreur confirmation demande de prêt: {e}")
        
        time.sleep(2)
        
        # Test 5: Email d'approbation de prêt
        print("\n📧 Test 5: Email d'approbation de prêt")
        try:
            result = FastECOBANKEmailService.send_loan_approval_fast(loan_request)
            print(f"✅ Email d'approbation envoyé: {result}")
        except Exception as e:
            print(f"❌ Erreur email d'approbation: {e}")
        
        time.sleep(2)
        
        # Test 6: Email d'activation de compte
        print("\n📧 Test 6: Email d'activation de compte")
        try:
            result = FastECOBANKEmailService.send_subscription_activated_fast(user)
            print(f"✅ Email d'activation envoyé: {result}")
        except Exception as e:
            print(f"❌ Erreur email d'activation: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 TOUS LES TESTS TERMINÉS")
        print("📧 Vérifiez votre boîte email pour voir les emails reçus")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_email_system()
