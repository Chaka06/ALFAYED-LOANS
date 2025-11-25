from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from decimal import Decimal
from .models import UserProfile, LoanRequest, Payment, Message, Notification
from .forms import CustomUserCreationForm, UserProfileForm, LoanRequestForm, MessageForm, NotificationForm
from .utils import generate_loan_certificate
from .email_service import InvestorEmailService
from .email_async import FastInvestorEmailService

def home(request):
    """Page d'accueil"""
    return render(request, 'loan_system/home.html')

def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

def register(request):
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Créer l'utilisateur (le profil sera créé automatiquement par le signal)
                    user = user_form.save()
                    
                    # Mettre à jour le profil avec les données du formulaire
                    profile = user.userprofile
                    profile.nom = profile_form.cleaned_data['nom']
                    profile.prenom = profile_form.cleaned_data['prenom']
                    profile.date_naissance = profile_form.cleaned_data['date_naissance']
                    profile.lieu_naissance = profile_form.cleaned_data['lieu_naissance']
                    profile.situation_matrimoniale = profile_form.cleaned_data['situation_matrimoniale']
                    profile.profession = profile_form.cleaned_data['profession']
                    profile.adresse = profile_form.cleaned_data['adresse']
                    profile.piece_identite_recto = profile_form.cleaned_data['piece_identite_recto']
                    profile.piece_identite_verso = profile_form.cleaned_data['piece_identite_verso']
                    profile.justificatif_adresse = profile_form.cleaned_data['justificatif_adresse']
                    if profile_form.cleaned_data['autre_document']:
                        profile.autre_document = profile_form.cleaned_data['autre_document']
                    
                    # Le profil reste non validé - seul l'admin peut valider
                    # if profile.is_complete():
                    #     profile.is_validated = True  # Auto-validation si profil complet
                    #     profile.date_validation = timezone.now()
                    
                    profile.save()
                    
                    # Envoyer l'email de bienvenue (rapide)
                    try:
                        FastInvestorEmailService.send_welcome_email_fast(user)
                    except Exception as e:
                        print(f"Erreur envoi email bienvenue: {e}")
                    
                    messages.success(request, 'Votre compte a été créé avec succès ! Un administrateur doit valider votre compte avant que vous puissiez faire des demandes de prêt.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création du compte: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'loan_system/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def dashboard(request):
    """Tableau de bord utilisateur"""
    # Envoyer notification de connexion seulement si c'est une nouvelle session
    if 'login_notification_sent' not in request.session:
        try:
            ip_address = request.META.get('REMOTE_ADDR', 'Non disponible')
            FastInvestorEmailService.send_login_alert_fast(request.user, ip_address)
            request.session['login_notification_sent'] = True
        except Exception as e:
            print(f"Erreur envoi notification connexion: {e}")
    
    # Récupérer ou créer le profil utilisateur
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if created:
        messages.info(request, 'Un profil a été créé pour vous. Veuillez le compléter.')
    
    loan_requests = LoanRequest.objects.filter(user=request.user).order_by('-date_demande')
    
    # Calculer les statistiques
    total_requests = loan_requests.count()
    approved_requests = loan_requests.filter(status='paye').count()
    pending_requests = loan_requests.filter(status__in=['en_attente', 'valide']).count()
    
    # Calculer le montant total accordé - Utiliser Decimal
    total_amount = Decimal('0.00')
    for loan in loan_requests.filter(status='paye'):
        total_amount += loan.montant
    
    context = {
        'profile': profile,
        'loan_requests': loan_requests,
        'stats': {
            'total': total_requests,
            'approved': approved_requests,
            'pending': pending_requests,
            'total_amount': total_amount,
        }
    }
    return render(request, 'loan_system/dashboard.html', context)

@login_required
def edit_profile(request):
    """Modifier le profil utilisateur"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'loan_system/edit_profile.html', {'form': form})

@login_required
def loan_request(request):
    """Formulaire de demande de prêt"""
    # Récupérer ou créer le profil utilisateur
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Vérifier si l'utilisateur est un superuser (pas besoin de validation)
    if not request.user.is_superuser:
        # Vérifier si le profil est complet
        if not profile.is_complete():
            messages.error(request, 'Votre profil doit être complet avant de faire une demande de prêt.')
            return redirect('edit_profile')
        
        # Vérifier si le profil est validé
        if not profile.is_validated:
            messages.error(request, 'Votre compte doit être validé par un administrateur avant de pouvoir faire une demande de prêt.')
            return redirect('dashboard')
    
    # Vérifier s'il y a déjà une demande en cours
    existing_request = LoanRequest.objects.filter(
        user=request.user, 
        status__in=['en_attente', 'valide']
    ).first()
    
    if existing_request:
        messages.warning(request, 'Vous avez déjà une demande de prêt en cours.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoanRequestForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    loan_req = form.save(commit=False)
                    loan_req.user = request.user
                    loan_req.save()
                    
                    # Envoyer confirmation de demande de prêt (rapide)
                    try:
                        FastInvestorEmailService.send_loan_request_confirmation_fast(loan_req)
                    except Exception as e:
                        print(f"Erreur envoi confirmation demande prêt: {e}")
                    
                    messages.success(request, 'Votre demande de prêt a été soumise avec succès ! Elle sera étudiée par nos équipes.')
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la soumission: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = LoanRequestForm()
    
    return render(request, 'loan_system/loan_request.html', {'form': form})

@login_required
def loan_detail(request, loan_id):
    """Détails d'une demande de prêt"""
    loan = get_object_or_404(LoanRequest, id=loan_id, user=request.user)
    return render(request, 'loan_system/loan_detail.html', {'loan': loan})

@login_required
def download_certificate(request, loan_id):
    """Télécharger l'attestation de prêt"""
    loan = get_object_or_404(LoanRequest, id=loan_id, user=request.user)
    
    if loan.status != 'paye':
        messages.error(request, 'L\'attestation n\'est disponible que pour les prêts payés.')
        return redirect('dashboard')
    
    try:
        # Vérifier que le profil est complet pour générer l'attestation
        if not loan.user.userprofile.is_complete():
            messages.error(request, 'Impossible de générer l\'attestation : profil utilisateur incomplet.')
            return redirect('dashboard')
        
        # Générer le PDF
        pdf_content = generate_loan_certificate(loan)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="attestation_pret_INV_{loan.id:06d}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération de l\'attestation: {str(e)}')
        return redirect('dashboard')

# === VUES DE MESSAGERIE ===

@login_required
def messages_list(request):
    """Liste des messages pour l'utilisateur connecté"""
    # Récupérer les messages reçus et envoyés
    received_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(received_messages, 10)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    # Statistiques
    unread_count = Message.objects.filter(recipient=request.user, status='non_lu').count()
    
    context = {
        'messages': messages_page,
        'sent_messages': sent_messages[:5],  # 5 derniers messages envoyés
        'unread_count': unread_count,
    }
    return render(request, 'loan_system/messages_list.html', context)

@login_required
def message_detail(request, message_id):
    """Détails d'un message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur peut voir ce message
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, 'Vous n\'avez pas accès à ce message.')
        return redirect('messages_list')
    
    # Marquer comme lu si c'est un message reçu
    if message.recipient == request.user and message.status == 'non_lu':
        message.mark_as_read()
    
    # Récupérer les réponses
    replies = Message.objects.filter(parent_message=message).order_by('created_at')
    
    context = {
        'message': message,
        'replies': replies,
    }
    return render(request, 'loan_system/message_detail.html', context)

@login_required
def send_message(request):
    """Envoyer un nouveau message"""
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            
            # Le destinataire est toujours le gestionnaire (premier superuser)
            from django.contrib.auth.models import User
            manager = User.objects.filter(is_superuser=True).first()
            if not manager:
                messages.error(request, 'Aucun gestionnaire trouvé.')
                return redirect('messages_list')
            
            message.recipient = manager
            message.save()
            
            messages.success(request, 'Votre message a été envoyé avec succès.')
            return redirect('message_detail', message_id=message.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        # Pré-remplir le formulaire avec les paramètres GET
        initial_data = {}
        if request.GET.get('subject'):
            initial_data['subject'] = request.GET.get('subject')
        if request.GET.get('content'):
            initial_data['content'] = request.GET.get('content')
        
        form = MessageForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'loan_system/send_message.html', context)

@login_required
def reply_message(request, message_id):
    """Répondre à un message"""
    parent_message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur peut répondre à ce message
    if parent_message.sender != request.user and parent_message.recipient != request.user:
        messages.error(request, 'Vous n\'avez pas accès à ce message.')
        return redirect('messages_list')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.parent_message = parent_message
            
            # Le destinataire est l'expéditeur du message parent
            reply.recipient = parent_message.sender
            reply.save()
            
            # Marquer le message parent comme répondu
            parent_message.mark_as_replied()
            
            messages.success(request, 'Votre réponse a été envoyée avec succès.')
            return redirect('message_detail', message_id=parent_message.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        # Pré-remplir le sujet avec "Re: "
        initial_subject = f"Re: {parent_message.subject}"
        form = MessageForm(initial={'subject': initial_subject})
    
    context = {
        'form': form,
        'parent_message': parent_message,
    }
    return render(request, 'loan_system/reply_message.html', context)

@login_required
def mark_message_read(request, message_id):
    """Marquer un message comme lu (AJAX)"""
    if request.method == 'POST':
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.mark_as_read()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def get_unread_count(request):
    """Récupérer le nombre de messages non lus (AJAX)"""
    unread_count = Message.objects.filter(recipient=request.user, status='non_lu').count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def admin_reply_message(request, message_id):
    """Répondre à un message depuis l'admin (pour les gestionnaires)"""
    if not request.user.is_staff:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    parent_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        # Traitement de la réponse depuis le formulaire inline
        subject = request.POST.get('subject', f"Re: {parent_message.subject}")
        content = request.POST.get('content', '')
        priority = request.POST.get('priority', 'normale')
        loan_request_id = request.POST.get('loan_request')
        
        if not content.strip():
            messages.error(request, 'Le contenu de la réponse ne peut pas être vide.')
            return redirect('admin:loan_system_message_change', message_id)
        
        # Créer la réponse
        reply = Message.objects.create(
            sender=request.user,
            recipient=parent_message.sender,
            subject=subject,
            content=content,
            priority=priority,
            parent_message=parent_message,
            loan_request_id=loan_request_id if loan_request_id else None
        )
        
        # Marquer le message parent comme répondu
        parent_message.mark_as_replied()
        
        messages.success(request, f'Votre réponse a été envoyée avec succès à {parent_message.sender.username}.')
        return redirect('admin:loan_system_message_change', message_id)
    
    # Redirection vers la page de modification du message
    return redirect('admin:loan_system_message_change', message_id)

@login_required
def change_password(request):
    """Changer le mot de passe de l'utilisateur"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            
            # Envoyer notification de changement de mot de passe (rapide)
            try:
                FastInvestorEmailService.send_password_change_alert_fast(request.user)
            except Exception as e:
                print(f"Erreur envoi notification changement mot de passe: {e}")
            
            messages.success(request, 'Votre mot de passe a été modifié avec succès.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'loan_system/change_password.html', context)

@login_required
def send_notification(request):
    """Envoyer une notification (pour les admins)"""
    if not request.user.is_superuser:
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    if request.method == 'POST':
        form = NotificationForm(request.POST, user=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.save()
            
            messages.success(request, f'Notification envoyée avec succès à {notification.recipient.username}.')
            return redirect('admin:loan_system_notification_changelist')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = NotificationForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'loan_system/send_notification.html', context)

@login_required
def notifications_list(request):
    """Liste des notifications pour l'utilisateur connecté"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    # Statistiques
    unread_count = Notification.objects.filter(recipient=request.user, status='non_lu').count()
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
    }
    return render(request, 'loan_system/notifications_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue (AJAX)"""
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def get_notification_count(request):
    """Récupérer le nombre de notifications non lues (AJAX)"""
    unread_count = Notification.objects.filter(recipient=request.user, status='non_lu').count()
    return JsonResponse({'unread_count': unread_count})