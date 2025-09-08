from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, LoanRequest

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
                'min': '5000000',
                'max': '50000000',
                'step': '100000',
                'placeholder': 'Entre 5 000 000 et 50 000 000 FCFA'
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
        if montant < 5000000:
            raise forms.ValidationError('Le montant minimum est de 5 000 000 FCFA')
        if montant > 50000000:
            raise forms.ValidationError('Le montant maximum est de 50 000 000 FCFA')
        return montant