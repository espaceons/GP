from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import MinValueValidator

class Domaine(models.Model):
    """Domaine de formation (ex: Informatique, Langues, Management)"""
    nom = models.CharField(_('Nom'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    couleur = models.CharField(_('Couleur'), max_length=7, default='#3498db')

    class Meta:
        verbose_name = _('Domaine')
        verbose_name_plural = _('Domaines')
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Formation(models.Model):
    """Programme de formation complet"""
    domaine = models.ForeignKey( Domaine, on_delete=models.PROTECT, verbose_name=_('Domaine'))
    reference = models.CharField(_('Référence'), max_length=20, unique=True)
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    objectifs = models.TextField(_('Objectifs pédagogiques'))
    public_cible = models.TextField(_('Public cible'))
    duree_jours = models.PositiveIntegerField(_('Durée (jours)'), validators=[MinValueValidator(1)])
    prix = models.DecimalField(_('Prix (€)'), max_digits=8, decimal_places=2)
    actif = models.BooleanField(_('Actif'), default=True)
    created_at = models.DateTimeField(_('Date création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Dernière modification'), auto_now=True)

    class Meta:
        verbose_name = _('Formation')
        verbose_name_plural = _('Formations')
        ordering = ['domaine', 'titre']

    def __str__(self):
        return f"{self.reference} - {self.titre}"

    def get_absolute_url(self):
        return reverse('formations:detail', kwargs={'pk': self.pk})

class Module(models.Model):
    """Module composant une formation"""
    formation = models.ForeignKey( Formation, on_delete=models.CASCADE, related_name='modules', verbose_name=_('Formation'))
    ordre = models.PositiveIntegerField(_('Ordre'))
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    duree_heures = models.PositiveIntegerField(_('Durée (heures)'))

    class Meta:
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
        ordering = ['formation', 'ordre']
        unique_together = [['formation', 'ordre'], ['formation', 'titre']]

    def __str__(self):
        return f"{self.formation.reference} - Module {self.ordre}: {self.titre}"