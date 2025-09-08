from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from .models import UserProfile, LoanRequest, Payment

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
                updated += 1
        self.message_user(request, f'{updated} profil(s) validé(s) avec succès.')
    validate_profiles.short_description = "Valider les profils sélectionnés"

@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ('get_reference', 'get_user_name', 'montant_formatted', 'status', 'date_demande', 'payment_key_display')
    list_filter = ('status', 'date_demande', 'date_validation')
    search_fields = ('user__username', 'user__userprofile__nom', 'user__userprofile__prenom', 'motif')
    readonly_fields = ('date_demande', 'montant_avance', 'payment_key', 'date_validation', 'date_paiement')
    
    def get_reference(self, obj):
        return f"ECO-{obj.id:06d}"
    get_reference.short_description = 'Référence'
    
    def get_user_name(self, obj):
        try:
            profile = obj.user.userprofile
            return f"{profile.nom} {profile.prenom}"
        except:
            return obj.user.username
    get_user_name.short_description = 'Nom complet'
    
    def montant_formatted(self, obj):
        return f"{obj.montant:,.0f} FCFA"
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
                updated += 1
        self.message_user(request, f'{updated} demande(s) validée(s) avec succès. Les clés de paiement ont été générées automatiquement.')
    validate_requests.short_description = "Valider les demandes sélectionnées"
    
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status='en_attente').update(status='rejete')
        self.message_user(request, f'{updated} demande(s) rejetée(s).')
    reject_requests.short_description = "Rejeter les demandes sélectionnées"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_loan_reference', 'get_user_name', 'payment_key_entered', 'validated_by', 'date_validation', 'is_key_valid')
    readonly_fields = ('date_validation',)
    list_filter = ('date_validation', 'validated_by')
    
    def get_loan_reference(self, obj):
        return f"ECO-{obj.loan_request.id:06d}"
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
                messages.success(request, f'Paiement validé avec succès ! Le prêt ECO-{obj.loan_request.id:06d} est maintenant actif.')
            else:
                messages.error(request, f'ATTENTION : La clé de paiement ne correspond pas pour le prêt ECO-{obj.loan_request.id:06d} !')
        super().save_model(request, obj, form, change)

# Réenregistrer l'admin User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration ECOBANK - Système de Prêts"
admin.site.site_title = "ECOBANK Admin"
admin.site.index_title = "Panneau de Gestion des Prêts en Ligne"