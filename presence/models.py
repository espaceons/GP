from django.db import models
from django.utils.translation import gettext_lazy as _
from planning.models import Cours
from eleves.models import Eleve

class Presence(models.Model):
    """Modèle pour enregistrer les présences aux cours"""
    cours = models.ForeignKey( Cours, on_delete=models.CASCADE, related_name='presences', verbose_name=_('Cours'))
    eleve = models.ForeignKey( Eleve, on_delete=models.CASCADE, related_name='presences', verbose_name=_('Élève'))
    present = models.BooleanField( _('Présent'), default=False, help_text=_("Cochez si l'élève était présent"))
    date_verification = models.DateTimeField( _('Date de vérification'), auto_now=True)
    remarque = models.TextField( _('Remarque'), blank=True, help_text=_("Remarque éventuelle sur la présence/absence"))

    class Meta:
        verbose_name = _('Présence')
        verbose_name_plural = _('Présences')
        unique_together = ('cours', 'eleve')
        ordering = ['cours__date', 'cours__heure_debut', 'eleve__user__last_name']

    def __str__(self):
        return f"{self.eleve} - {self.cours} ({'Présent' if self.present else 'Absent'})"

class StatutPresence(models.Model):
    """Modèle pour les différents statuts de présence"""
    nom = models.CharField(_('Nom'), max_length=50)
    code = models.CharField(_('Code'), max_length=10, unique=True)
    est_present = models.BooleanField(_('Est présent'), default=True)
    couleur = models.CharField(_('Couleur'), max_length=7, default='#28a745')

    class Meta:
        verbose_name = _('Statut de présence')
        verbose_name_plural = _('Statuts de présence')

    def __str__(self):
        return self.nom