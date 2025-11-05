#!/usr/bin/env python
"""
Script de test pour le système d'emails ECOBANK
Teste l'envoi de tous les types d'emails automatiques
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.contrib.auth.models import User
from loan_system.models import UserProfile, LoanRequest
from loan_system.email_service import ECOBANKEmailService
from decimal import Decimal

def test_email_system():
    """Test complet du système d'emails"""
    print("🧪 TEST DU SYSTÈME D'EMAILS ECOBANK")
    print("=" * 50)
    
    # Créer un utilisateur de test
    try:
        user, created = User.objects.get_or_create(
            username='test_email_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
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
        
        # Test 1: Email de bienvenue
        print("\n📧 Test 1: Email de bienvenue")
        try:
            result = ECOBANKEmailService.send_welcome_email(user)
            if result:
                print("✅ Email de bienvenue envoyé avec succès")
            else:
                print("❌ Échec envoi email de bienvenue")
        except Exception as e:
            print(f"❌ Erreur email de bienvenue: {e}")
        
        # Test 2: Notification de connexion
        print("\n📧 Test 2: Notification de connexion")
        try:
            result = ECOBANKEmailService.send_login_notification(user, "192.168.1.100")
            if result:
                print("✅ Notification de connexion envoyée avec succès")
            else:
                print("❌ Échec envoi notification de connexion")
        except Exception as e:
            print(f"❌ Erreur notification de connexion: {e}")
        
        # Test 3: Alerte changement de mot de passe
        print("\n📧 Test 3: Alerte changement de mot de passe")
        try:
            result = ECOBANKEmailService.send_password_change_alert(user)
            if result:
                print("✅ Alerte changement mot de passe envoyée avec succès")
            else:
                print("❌ Échec envoi alerte changement mot de passe")
        except Exception as e:
            print(f"❌ Erreur alerte changement mot de passe: {e}")
        
        # Test 4: Email de réinitialisation de mot de passe
        print("\n📧 Test 4: Email de réinitialisation de mot de passe")
        try:
            reset_link = "http://localhost:9000/reset-password/token123/"
            result = ECOBANKEmailService.send_password_reset_email(user, reset_link)
            if result:
                print("✅ Email de réinitialisation envoyé avec succès")
            else:
                print("❌ Échec envoi email de réinitialisation")
        except Exception as e:
            print(f"❌ Erreur email de réinitialisation: {e}")
        
        # Créer une demande de prêt pour les tests suivants
        loan_request, created = LoanRequest.objects.get_or_create(
            user=user,
            defaults={
                'montant': Decimal('10000000'),  # 10 millions
                'motif': 'Test email system',
                'document_projet': None,  # Pas de document pour le test
                'status': 'valide',
                'duree_remboursement_mois': 12
            }
        )
        
        if created:
            print("✅ Demande de prêt de test créée")
        
        # Test 5: Confirmation de demande de prêt
        print("\n📧 Test 5: Confirmation de demande de prêt")
        try:
            result = ECOBANKEmailService.send_loan_request_confirmation(loan_request)
            if result:
                print("✅ Confirmation demande de prêt envoyée avec succès")
            else:
                print("❌ Échec envoi confirmation demande de prêt")
        except Exception as e:
            print(f"❌ Erreur confirmation demande de prêt: {e}")
        
        # Test 6: Email d'approbation de prêt
        print("\n📧 Test 6: Email d'approbation de prêt")
        try:
            result = ECOBANKEmailService.send_loan_approval_email(loan_request)
            if result:
                print("✅ Email d'approbation envoyé avec succès")
            else:
                print("❌ Échec envoi email d'approbation")
        except Exception as e:
            print(f"❌ Erreur email d'approbation: {e}")
        
        # Test 7: Email d'activation de compte
        print("\n📧 Test 7: Email d'activation de compte")
        try:
            result = ECOBANKEmailService.send_subscription_activated_email(user)
            if result:
                print("✅ Email d'activation envoyé avec succès")
            else:
                print("❌ Échec envoi email d'activation")
        except Exception as e:
            print(f"❌ Erreur email d'activation: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 TESTS TERMINÉS")
        print("Vérifiez votre boîte email pour voir les résultats")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_email_system()
