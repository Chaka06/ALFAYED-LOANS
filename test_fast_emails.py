#!/usr/bin/env python
"""
Test rapide du système d'emails ECOBANK optimisé
Teste la vitesse d'envoi avec le nouveau design
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

def test_fast_emails():
    """Test rapide du système d'emails optimisé"""
    print("🚀 TEST RAPIDE DU SYSTÈME D'EMAILS ECOBANK")
    print("=" * 60)
    
    start_time = time.time()
    
    # Créer un utilisateur de test
    try:
        user, created = User.objects.get_or_create(
            username='test_fast_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Fast'
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
        
        # Test 1: Email de bienvenue (rapide)
        print("\n📧 Test 1: Email de bienvenue (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_welcome_email_fast(user)
            test_end = time.time()
            if result:
                print(f"✅ Email de bienvenue envoyé en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi email de bienvenue")
        except Exception as e:
            print(f"❌ Erreur email de bienvenue: {e}")
        
        # Test 2: Notification de connexion (rapide)
        print("\n📧 Test 2: Notification de connexion (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_login_alert_fast(user, "192.168.1.100")
            test_end = time.time()
            if result:
                print(f"✅ Notification de connexion envoyée en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi notification de connexion")
        except Exception as e:
            print(f"❌ Erreur notification de connexion: {e}")
        
        # Test 3: Alerte changement de mot de passe (rapide)
        print("\n📧 Test 3: Alerte changement de mot de passe (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_password_change_alert_fast(user)
            test_end = time.time()
            if result:
                print(f"✅ Alerte changement mot de passe envoyée en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi alerte changement mot de passe")
        except Exception as e:
            print(f"❌ Erreur alerte changement mot de passe: {e}")
        
        # Créer une demande de prêt pour les tests suivants
        loan_request, created = LoanRequest.objects.get_or_create(
            user=user,
            defaults={
                'montant': Decimal('10000000'),  # 10 millions
                'motif': 'Test email system rapide',
                'document_projet': None,
                'status': 'valide',
                'duree_remboursement_mois': 12
            }
        )
        
        if created:
            print("✅ Demande de prêt de test créée")
        
        # Test 4: Confirmation de demande de prêt (rapide)
        print("\n📧 Test 4: Confirmation de demande de prêt (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_loan_request_confirmation_fast(loan_request)
            test_end = time.time()
            if result:
                print(f"✅ Confirmation demande de prêt envoyée en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi confirmation demande de prêt")
        except Exception as e:
            print(f"❌ Erreur confirmation demande de prêt: {e}")
        
        # Test 5: Email d'approbation de prêt (rapide)
        print("\n📧 Test 5: Email d'approbation de prêt (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_loan_approval_fast(loan_request)
            test_end = time.time()
            if result:
                print(f"✅ Email d'approbation envoyé en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi email d'approbation")
        except Exception as e:
            print(f"❌ Erreur email d'approbation: {e}")
        
        # Test 6: Email d'activation de compte (rapide)
        print("\n📧 Test 6: Email d'activation de compte (RAPIDE)")
        test_start = time.time()
        try:
            result = FastECOBANKEmailService.send_subscription_activated_fast(user)
            test_end = time.time()
            if result:
                print(f"✅ Email d'activation envoyé en {test_end - test_start:.2f}s")
            else:
                print("❌ Échec envoi email d'activation")
        except Exception as e:
            print(f"❌ Erreur email d'activation: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"🎉 TESTS TERMINÉS EN {total_time:.2f} SECONDES")
        print("🚀 SYSTÈME D'EMAILS ECOBANK OPTIMISÉ")
        print("📧 Design professionnel + Envoi rapide")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_fast_emails()
