from django import forms
from django.utils.translation import gettext_lazy as _
from eleves.models import Eleve
from presence.models import Presence

class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ['present', 'remarque']
        widgets = {
            'remarque': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'present': _('Présent'),
            'remarque': _('Remarque'),
        }

class BulkPresenceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        eleves = kwargs.pop('eleves', [])
        cours = kwargs.pop('cours', None)
        super().__init__(*args, **kwargs)

        for eleve in eleves:
            field_name = f'presence_{eleve.eleve.id}'
            initial = Presence.objects.filter(
                cours=cours,
                eleve=eleve.eleve
            ).first()
            self.fields[field_name] = forms.BooleanField(
                label=f"{eleve.eleve.user.get_full_name()}",
                required=False,
                initial=initial.present if initial else False
            )