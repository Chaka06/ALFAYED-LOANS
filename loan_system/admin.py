from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.shortcuts import redirect
from .models import UserProfile, LoanRequest, Payment, Message, Notification
from .email_async import FastECOBANKEmailService

# Inline pour UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Utilisateur'
    readonly_fields = ('date_creation',)
    extra = 0

# Extension de l'admin User
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_validation_status')
    
    def get_validation_status(self, obj):
        try:
            profile = obj.userprofile
            if profile.is_validated:
                return format_html('<span style="color: green; font-weight: bold;">✓ Validé</span>')
            else:
                return format_html('<span style="color: red; font-weight: bold;">✗ Non validé</span>')
        except UserProfile.DoesNotExist:
            return format_html('<span style="color: orange; font-weight: bold;">⚠ Profil incomplet</span>')
    
    get_validation_status.short_description = 'Statut de validation'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'profession', 'is_validated', 'date_creation')
    list_filter = ('is_validated', 'situation_matrimoniale', 'date_creation')
    search_fields = ('nom', 'prenom', 'profession', 'user__username')
    readonly_fields = ('date_creation', 'date_validation')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'lieu_naissance', 
                      'situation_matrimoniale', 'profession', 'adresse')
        }),
        ('Documents', {
            'fields': ('piece_identite_recto', 'piece_identite_verso', 
                      'justificatif_adresse', 'autre_document')
        }),
        ('Validation', {
            'fields': ('is_validated', 'date_creation', 'date_validation')
        }),
    )
    
    actions = ['validate_profiles']
    
    def validate_profiles(self, request, queryset):
        updated = 0
        for profile in queryset:
            if not profile.is_validated:
                profile.is_validated = True
                profile.date_validation = timezone.now()
                profile.save()
                
                # Envoyer email d'activation
                try:
                    FastECOBANKEmailService.send_subscription_activated_fast(profile.user)
                except Exception as e:
                    print(f"Erreur envoi email activation: {e}")
                
                updated += 1
        self.message_user(request, f'{updated} profil(s) validé(s) avec succès. Les emails d\'activation ont été envoyés.')
    validate_profiles.short_description = "Valider les profils sélectionnés"

@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ('get_reference', 'get_user_name', 'montant_formatted', 'status', 'date_demande', 'payment_key_display')
    list_filter = ('status', 'date_demande', 'date_validation')
    search_fields = ('user__username', 'user__userprofile__nom', 'user__userprofile__prenom', 'motif')
    readonly_fields = ('date_demande', 'montant_avance', 'payment_key', 'date_validation', 'date_paiement')
    
    def save_model(self, request, obj, form, change):
        """Surcharge pour détecter les changements de statut et envoyer un email"""
        old_status = None
        if change and obj.pk:
            try:
                old_obj = LoanRequest.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except LoanRequest.DoesNotExist:
                pass
        
        # Sauvegarder l'objet
        super().save_model(request, obj, form, change)
        
        # Si le statut a changé, envoyer un email
        if change and old_status and old_status != obj.status:
            try:
                FastECOBANKEmailService.send_status_change_email_fast(obj, old_status, obj.status)
            except Exception as e:
                print(f"Erreur envoi email changement statut: {e}")
    
    def get_reference(self, obj):
        return f"INV-{obj.id:06d}"
    get_reference.short_description = 'Référence'
    
    def get_user_name(self, obj):
        try:
            profile = obj.user.userprofile
            return f"{profile.nom} {profile.prenom}"
        except:
            return obj.user.username
    get_user_name.short_description = 'Nom complet'
    
    def montant_formatted(self, obj):
        return f"{obj.montant:,.2f} €"
    montant_formatted.short_description = 'Montant'
    
    def payment_key_display(self, obj):
        if obj.payment_key and obj.status == 'valide':
            return format_html(
                '<span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 4px; font-family: monospace;">{}</span>',
                obj.payment_key
            )
        return obj.payment_key or '-'
    payment_key_display.short_description = 'Clé de paiement'
    
    fieldsets = (
        ('Référence', {
            'fields': ('user',),
            'description': 'Informations de base de la demande'
        }),
        ('Détails du prêt', {
            'fields': ('montant', 'montant_avance', 'motif', 'document_projet'),
            'description': 'Montant et justification du prêt'
        }),
        ('Statut et validation', {
            'fields': ('status', 'date_demande', 'date_validation'),
            'description': 'Suivi de la demande'
        }),
        ('Paiement et remboursement', {
            'fields': ('payment_key', 'date_paiement', 'duree_remboursement_mois'),
            'description': 'Informations de paiement et remboursement'
        }),
    )
    
    actions = ['validate_requests', 'reject_requests']
    
    def validate_requests(self, request, queryset):
        updated = 0
        for loan_request in queryset:
            if loan_request.status == 'en_attente':
                loan_request.status = 'valide'
                loan_request.date_validation = timezone.now()
                loan_request.save()
                
                # Envoyer email d'approbation
                try:
                    FastECOBANKEmailService.send_loan_approval_fast(loan_request)
                except Exception as e:
                    print(f"Erreur envoi email approbation: {e}")
                
                updated += 1
        self.message_user(request, f'{updated} demande(s) validée(s) avec succès. Les emails d\'approbation ont été envoyés.')
    validate_requests.short_description = "Valider les demandes sélectionnées"
    
    def reject_requests(self, request, queryset):
        updated = 0
        for loan_request in queryset.filter(status='en_attente'):
            loan_request.status = 'rejete'
            loan_request.save()
            
            # Envoyer email de rejet
            try:
                FastECOBANKEmailService.send_loan_rejection_fast(loan_request)
            except Exception as e:
                print(f"Erreur envoi email rejet: {e}")
            
            updated += 1
        self.message_user(request, f'{updated} demande(s) rejetée(s). Les emails de rejet ont été envoyés.')
    reject_requests.short_description = "Rejeter les demandes sélectionnées"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_loan_reference', 'get_user_name', 'payment_key_entered', 'validated_by', 'date_validation', 'is_key_valid')
    readonly_fields = ('date_validation',)
    list_filter = ('date_validation', 'validated_by')
    
    def get_loan_reference(self, obj):
        return f"INV-{obj.loan_request.id:06d}"
    get_loan_reference.short_description = 'Référence prêt'
    
    def get_user_name(self, obj):
        try:
            profile = obj.loan_request.user.userprofile
            return f"{profile.nom} {profile.prenom}"
        except:
            return obj.loan_request.user.username
    get_user_name.short_description = 'Client'
    
    def is_key_valid(self, obj):
        if obj.payment_key_entered == obj.loan_request.payment_key:
            return format_html('<span style="color: green; font-weight: bold;">✓ Valide</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Invalide</span>')
    is_key_valid.short_description = 'Clé valide'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nouveau paiement
            obj.validated_by = request.user
            # Vérifier que la clé correspond
            if obj.payment_key_entered == obj.loan_request.payment_key:
                obj.loan_request.status = 'paye'
                obj.loan_request.date_paiement = timezone.now()
                obj.loan_request.save()
                obj.date_validation = timezone.now()
                obj.save()
                
                # Envoyer email de confirmation de paiement
                try:
                    FastECOBANKEmailService.send_payment_confirmation_fast(obj.loan_request, obj)
                except Exception as e:
                    print(f"Erreur envoi email confirmation paiement: {e}")
                
                messages.success(request, f'Paiement validé avec succès ! Le prêt INV-{obj.loan_request.id:06d} est maintenant actif. Un email de confirmation a été envoyé.')
            else:
                messages.error(request, f'ATTENTION : La clé de paiement ne correspond pas pour le prêt INV-{obj.loan_request.id:06d} !')
        super().save_model(request, obj, form, change)

# Réenregistrer l'admin User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_subject', 'get_sender', 'get_recipient', 'priority', 'status', 'created_at', 'get_loan_reference', 'get_reply_link')
    list_filter = ('status', 'priority', 'created_at', 'sender__is_staff')
    search_fields = ('subject', 'content', 'sender__username', 'recipient__username')
    readonly_fields = ('created_at', 'read_at', 'time_since_created')
    ordering = ['-created_at']
    change_form_template = 'admin/loan_system/message/change_form.html'
    
    fieldsets = (
        ('Message', {
            'fields': ('sender', 'recipient', 'subject', 'content')
        }),
        ('Métadonnées', {
            'fields': ('priority', 'status', 'loan_request', 'parent_message')
        }),
        ('Dates', {
            'fields': ('created_at', 'read_at', 'time_since_created'),
            'classes': ('collapse',)
        }),
    )
    
    def get_subject(self, obj):
        if obj.status == 'non_lu':
            return format_html('<strong>{}</strong>', obj.subject)
        return obj.subject
    get_subject.short_description = 'Sujet'
    
    def get_sender(self, obj):
        if obj.is_from_manager:
            return format_html('<span style="color: #008751; font-weight: bold;">👨‍💼 Gestionnaire</span>')
        else:
            try:
                profile = obj.sender.userprofile
                name = f"{profile.prenom} {profile.nom}" if profile.prenom and profile.nom else obj.sender.username
                return format_html('<span style="color: #007bff;">👤 {}</span>', name)
            except:
                return format_html('<span style="color: #007bff;">👤 {}</span>', obj.sender.username)
    get_sender.short_description = 'Expéditeur'
    
    def get_recipient(self, obj):
        if obj.recipient.is_staff:
            return format_html('<span style="color: #008751; font-weight: bold;">👨‍💼 Gestionnaire</span>')
        else:
            try:
                profile = obj.recipient.userprofile
                name = f"{profile.prenom} {profile.nom}" if profile.prenom and profile.nom else obj.recipient.username
                return format_html('<span style="color: #007bff;">👤 {}</span>', name)
            except:
                return format_html('<span style="color: #007bff;">👤 {}</span>', obj.recipient.username)
    get_recipient.short_description = 'Destinataire'
    
    def get_loan_reference(self, obj):
        if obj.loan_request:
            url = reverse('admin:loan_system_loanrequest_change', args=[obj.loan_request.id])
            return format_html('<a href="{}" target="_blank">INV-{:06d}</a>', url, obj.loan_request.id)
        return '-'
    get_loan_reference.short_description = 'Prêt lié'
    
    def get_reply_link(self, obj):
        """Lien pour répondre au message"""
        # Seuls les superusers peuvent répondre
        url = reverse('admin_reply_message', args=[obj.id])
        return format_html('<a href="{}" class="button" title="Répondre au message">📝 Répondre</a>', url)
    get_reply_link.short_description = 'Actions'
    
    def get_queryset(self, request):
        # Les superusers voient tous les messages
        if request.user.is_superuser:
            return super().get_queryset(request)
        # Les autres utilisateurs ne voient que leurs messages
        return super().get_queryset(request).filter(
            models.Q(sender=request.user) | models.Q(recipient=request.user)
        )
    
    actions = ['mark_as_read', 'mark_as_replied', 'set_high_priority', 'reply_to_message']
    
    def reply_to_message(self, request, queryset):
        """Répondre aux messages sélectionnés"""
        if queryset.count() != 1:
            self.message_user(request, 'Veuillez sélectionner exactement un message pour répondre.')
            return
        
        message = queryset.first()
        return redirect('admin_reply_message', message_id=message.id)
    reply_to_message.short_description = "Répondre au message"
    
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(status='non_lu').update(status='lu', read_at=timezone.now())
        self.message_user(request, f'{updated} message(s) marqué(s) comme lu(s).')
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='repondu')
        self.message_user(request, f'{updated} message(s) marqué(s) comme répondu(s).')
    mark_as_replied.short_description = "Marquer comme répondu"
    
    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority='haute')
        self.message_user(request, f'{updated} message(s) marqué(s) comme haute priorité.')
    set_high_priority.short_description = "Marquer haute priorité"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_recipient', 'notification_type', 'status', 'created_at', 'get_sender')
    list_filter = ('status', 'notification_type', 'created_at', 'sender__is_staff')
    search_fields = ('title', 'content', 'recipient__username', 'sender__username')
    readonly_fields = ('created_at', 'read_at', 'time_since_created')
    ordering = ['-created_at']
    
    fieldsets = (
        ('Notification', {
            'fields': ('recipient', 'title', 'content', 'notification_type')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('sender', 'status', 'created_at', 'read_at', 'time_since_created'),
            'classes': ('collapse',)
        }),
    )
    
    def get_title(self, obj):
        if obj.status == 'non_lu':
            return format_html('<strong>{}</strong>', obj.title)
        return obj.title
    get_title.short_description = 'Titre'
    
    def get_recipient(self, obj):
        try:
            profile = obj.recipient.userprofile
            name = f"{profile.prenom} {profile.nom}" if profile.prenom and profile.nom else obj.recipient.username
            return format_html('<span style="color: #007bff;">👤 {}</span>', name)
        except:
            return format_html('<span style="color: #007bff;">👤 {}</span>', obj.recipient.username)
    get_recipient.short_description = 'Destinataire'
    
    def get_sender(self, obj):
        if obj.sender.is_staff:
            return format_html('<span style="color: #008751; font-weight: bold;">👨‍💼 Admin</span>')
        else:
            return format_html('<span style="color: #007bff;">👤 {}</span>', obj.sender.username)
    get_sender.short_description = 'Expéditeur'
    
    def get_queryset(self, request):
        # Les superusers voient toutes les notifications
        if request.user.is_superuser:
            return super().get_queryset(request)
        # Les autres utilisateurs ne voient que leurs notifications
        return super().get_queryset(request).filter(recipient=request.user)
    
    actions = ['mark_as_read', 'mark_as_archived', 'send_notification_action']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(status='non_lu').update(status='lu', read_at=timezone.now())
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_archived(self, request, queryset):
        updated = queryset.update(status='archive')
        self.message_user(request, f'{updated} notification(s) archivée(s).')
    mark_as_archived.short_description = "Archiver"
    
    def send_notification_action(self, request, queryset):
        return redirect('send_notification')
    send_notification_action.short_description = "Envoyer une notification"

# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration Investor Banque - Système de Prêts"
admin.site.site_title = "Investor Banque Admin"
admin.site.index_title = "Panneau de Gestion des Prêts en Ligne"