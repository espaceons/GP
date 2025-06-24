from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from .models import Eleve, DocumentEleve

class EleveUpdateForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            'date_naissance',
            'telephone',
            'adresse',
            'ville',
            'code_postal',
            'pays'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'date_naissance': _('Date de naissance'),
            'telephone': _('Téléphone'),
            'adresse': _('Adresse complète'),
            'ville': _('Ville'),
            'code_postal': _('Code postal'),
            'pays': _('Pays'),
        }

class DocumentEleveForm(forms.ModelForm):
    class Meta:
        model = DocumentEleve
        fields = ['type_document', 'fichier']
        widgets = {
        }
        labels = {
            'type_document': _('Type de document'),
            'fichier': _('Fichier à uploader'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichier'].validators.append(
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
                message=_("Seuls les fichiers PDF, Word et images sont acceptés")
            )
        )