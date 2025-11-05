from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, LoanRequest, Message, Notification

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance',
            'situation_matrimoniale', 'profession', 'adresse',
            'piece_identite_recto', 'piece_identite_verso',
            'justificatif_adresse', 'autre_document'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'situation_matrimoniale': forms.Select(attrs={'class': 'form-control'}),
            'piece_identite_recto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'piece_identite_verso': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'justificatif_adresse': forms.FileInput(attrs={'class': 'form-control'}),
            'autre_document': forms.FileInput(attrs={'class': 'form-control'}),
        }

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['montant', 'motif', 'document_projet']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5000',
                'max': '5000000',
                'step': '100',
                'placeholder': 'Entre 5 000 et 5 000 000 EUR'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Décrivez le motif de votre demande de prêt...'
            }),
            'document_projet': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }
    
    def clean_montant(self):
        montant = self.cleaned_data['montant']
        if montant < 5000:
            raise forms.ValidationError('Le montant minimum est de 5 000 EUR')
        if montant > 5000000:
            raise forms.ValidationError('Le montant maximum est de 5 000 000 EUR')
        return montant

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content', 'priority', 'loan_request']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de votre message...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Décrivez votre demande ou question...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'loan_request': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les demandes de prêt de l'utilisateur
        if user and not user.is_superuser:
            self.fields['loan_request'].queryset = LoanRequest.objects.filter(user=user)
        elif user and user.is_superuser:
            self.fields['loan_request'].queryset = LoanRequest.objects.all()
        else:
            self.fields['loan_request'].queryset = LoanRequest.objects.none()
        
        # Rendre le champ loan_request optionnel
        self.fields['loan_request'].required = False
        self.fields['loan_request'].empty_label = "Aucune demande de prêt liée"
    
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 10:
            raise forms.ValidationError('Le message doit contenir au moins 10 caractères.')
        return content

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'title', 'content', 'notification_type', 'action_url', 'action_text']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Sélectionner un utilisateur...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la notification...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Contenu de la notification...'
            }),
            'notification_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'action_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://exemple.com (optionnel)'
            }),
            'action_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texte du lien (optionnel)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les utilisateurs (exclure les superusers)
        if user and user.is_superuser:
            self.fields['recipient'].queryset = User.objects.filter(is_superuser=False)
        else:
            self.fields['recipient'].queryset = User.objects.none()
    
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 5:
            raise forms.ValidationError('Le contenu doit contenir au moins 5 caractères.')
        return content