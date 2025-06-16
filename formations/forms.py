from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Formation, Module

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = [
            'domaine', 'reference', 'titre', 'description', 
            'objectifs', 'public_cible', 'duree_jours', 'prix', 'actif'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'objectifs': forms.Textarea(attrs={'rows': 4}),
            'public_cible': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'actif': _('Formation active'),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['formation', 'ordre', 'titre', 'description', 'duree_heures']
        widgets = {
            'formation': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }