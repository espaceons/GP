from django import forms
from .models import Document
from django.utils.translation import gettext_lazy as _

class DocumentForm(forms.ModelForm):
    """
    Formulaire pour la création et la modification de documents.
    Gère la validation pour s'assurer qu'un fichier ou une URL est soumis, mais pas les deux.
    """
    class Meta:
        model = Document
        fields = [
            'titre', 
            'fichier', 
            'url', 
            'type_document', # Bien que auto-détecté, utile pour la sélection initiale ou la modification manuelle
            'description', 
            'formations', 
            'visible_eleves', 
            'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'formations': forms.CheckboxSelectMultiple(), # Pour permettre la sélection multiple de formations
        }
        labels = {
            'titre': _('Titre du document'),
            'fichier': _('Fichier à télécharger'),
            'url': _('Lien externe (URL)'),
            'type_document': _('Type de document'),
            'description': _('Description'),
            'formations': _('Formations associées'),
            'visible_eleves': _('Visible par les élèves'),
            'tags': _('Mots-clés (séparés par des virgules)'),
        }
        help_texts = {
            'fichier': _("Téléchargez un fichier. Si vous fournissez une URL, laissez ce champ vide."),
            'url': _("Saisissez une URL. Si vous téléchargez un fichier, laissez ce champ vide."),
        }

    def clean(self):
        """
        Validation personnalisée pour s'assurer que soit 'fichier', soit 'url' est renseigné, mais pas les deux.
        """
        cleaned_data = super().clean()
        fichier = cleaned_data.get('fichier')
        url = cleaned_data.get('url')

        if not fichier and not url:
            # Si ni fichier ni url n'est fourni
            raise forms.ValidationError(
                _("Vous devez fournir soit un fichier, soit une URL pour le document."),
                code='no_file_or_url'
            )
        elif fichier and url:
            # Si les deux sont fournis
            raise forms.ValidationError(
                _("Vous ne pouvez pas fournir à la fois un fichier et une URL pour le document."),
                code='both_file_and_url'
            )
        
        # Le type de document sera défini dans la méthode save du modèle, 
        # mais on s'assure que si un fichier est là, le type_document correspond bien à l'extension
        # et vice versa pour l'URL. Cela est géré par la méthode save du modèle, donc pas besoin ici.
        return cleaned_data

