from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_eleve', 'is_formateur')
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_eleve', 'is_formateur')
        
class EleveRegistrationForm(UserCreationForm):
    date_naissance = forms.DateField(required=False, help_text="Date de naissance de l'élève.")
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_eleve')
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
class FormateurRegistrationForm(UserCreationForm):
    specialite = forms.CharField(max_length=200, label=_('Spécialité'))
    bio = forms.CharField(widget=forms.Textarea, label=_('Biographie'))
    matricule = forms.CharField(max_length=20, label=_('Matricule'))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']