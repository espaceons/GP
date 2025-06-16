from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Cours, Disponibilite

class CoursForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        formateur = kwargs.pop('formateur', None)
        super().__init__(*args, **kwargs)
        
        if formateur:
            self.fields['formation'].queryset = formateur.formations.all()

    class Meta:
        model = Cours
        fields = [
            'formation', 'titre', 'date', 'heure_debut', 'heure_fin',
            'salle', 'description', 'objectifs', 'materiel_requis', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'objectifs': forms.Textarea(attrs={'rows': 3}),
            'materiel_requis': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = Disponibilite
        fields = ['date_debut', 'date_fin', 'type', 'notes']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }