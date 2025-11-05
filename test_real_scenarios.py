#!/usr/bin/env python
"""
Test des scénarios réels d'envoi d'emails ECOBANK
Simule les actions utilisateur réelles
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

def test_real_scenarios():
    """Test des scénarios réels"""
    print("🎯 TEST SCÉNARIOS RÉELS ECOBANK")
    print("=" * 60)
    
    # Scénario 1: Inscription d'un nouvel utilisateur
    print("\n👤 SCÉNARIO 1: Inscription nouvel utilisateur")
    try:
        # Créer un utilisateur (simule l'inscription)
        user = User.objects.create_user(
            username='nouveau_client',
            email='nouveau@example.com',
            password='motdepasse123',
            first_name='Marie',
            last_name='Kouassi'
        )
        
        # Créer le profil (simule le formulaire d'inscription)
        profile = UserProfile.objects.create(
            user=user,
            prenom='Marie',
            nom='Kouassi',
            telephone='+225 07 12 34 56 78',
            adresse='Abidjan, Côte d\'Ivoire',
            profession='Commerçante',
            revenus_mensuels=300000,
            is_validated=False
        )
        
        print("✅ Utilisateur et profil créés")
        
        # Envoyer email de bienvenue (comme dans la vue register)
        result = FastECOBANKEmailService.send_welcome_email_fast(user)
        print(f"✅ Email de bienvenue envoyé: {result}")
        
    except Exception as e:
        print(f"❌ Erreur scénario 1: {e}")
    
    time.sleep(3)
    
    # Scénario 2: Connexion utilisateur
    print("\n🔐 SCÉNARIO 2: Connexion utilisateur")
    try:
        # Simuler la connexion (comme dans la vue dashboard)
        result = FastECOBANKEmailService.send_login_alert_fast(user, "192.168.1.50")
        print(f"✅ Notification de connexion envoyée: {result}")
        
    except Exception as e:
        print(f"❌ Erreur scénario 2: {e}")
    
    time.sleep(3)
    
    # Scénario 3: Demande de prêt
    print("\n💰 SCÉNARIO 3: Demande de prêt")
    try:
        # Créer une demande de prêt (comme dans la vue loan_request)
        loan_request = LoanRequest.objects.create(
            user=user,
            montant=Decimal('15000000'),  # 15 millions
            motif='Achat de matériel pour mon commerce',
            document_projet=None,
            status='en_attente',
            duree_remboursement_mois=24
        )
        
        print("✅ Demande de prêt créée")
        
        # Envoyer confirmation (comme dans la vue loan_request)
        result = FastECOBANKEmailService.send_loan_request_confirmation_fast(loan_request)
        print(f"✅ Confirmation demande de prêt envoyée: {result}")
        
    except Exception as e:
        print(f"❌ Erreur scénario 3: {e}")
    
    time.sleep(3)
    
    # Scénario 4: Validation par l'admin
    print("\n👨‍💼 SCÉNARIO 4: Validation par l'admin")
    try:
        # Simuler la validation du profil par l'admin
        profile.is_validated = True
        profile.save()
        
        # Envoyer email d'activation
        result = FastECOBANKEmailService.send_subscription_activated_fast(user)
        print(f"✅ Email d'activation envoyé: {result}")
        
        # Simuler l'approbation du prêt par l'admin
        loan_request.status = 'valide'
        loan_request.save()
        
        # Envoyer email d'approbation
        result = FastECOBANKEmailService.send_loan_approval_fast(loan_request)
        print(f"✅ Email d'approbation envoyé: {result}")
        
    except Exception as e:
        print(f"❌ Erreur scénario 4: {e}")
    
    time.sleep(3)
    
    # Scénario 5: Changement de mot de passe
    print("\n🔒 SCÉNARIO 5: Changement de mot de passe")
    try:
        # Simuler le changement de mot de passe
        result = FastECOBANKEmailService.send_password_change_alert_fast(user)
        print(f"✅ Alerte changement mot de passe envoyée: {result}")
        
    except Exception as e:
        print(f"❌ Erreur scénario 5: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES SCÉNARIOS TERMINÉS")
    print("📧 Vérifiez votre boîte email pour voir tous les emails")
    print("📋 Résumé des emails envoyés:")
    print("   1. Email de bienvenue (inscription)")
    print("   2. Notification de connexion")
    print("   3. Confirmation de demande de prêt")
    print("   4. Email d'activation de compte")
    print("   5. Email d'approbation de prêt")
    print("   6. Alerte changement de mot de passe")
    print("=" * 60)

if __name__ == "__main__":
    test_real_scenarios()
