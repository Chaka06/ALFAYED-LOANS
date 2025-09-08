from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import UserProfile, LoanRequest, Payment
from .forms import CustomUserCreationForm, UserProfileForm, LoanRequestForm
from .utils import generate_loan_certificate

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
                    profile.save()
                    
                    messages.success(request, 'Votre compte a été créé avec succès ! Il doit maintenant être validé par un administrateur.')
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
        response['Content-Disposition'] = f'attachment; filename="attestation_pret_ECO_{loan.id:06d}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération de l\'attestation: {str(e)}')
        return redirect('dashboard')