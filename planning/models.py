import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from formations.models import Formation
from formateurs.models import Formateur
from django.urls import reverse

class Salle(models.Model):
    """Modèle pour les salles de formation"""
    nom = models.CharField(_('Nom'), max_length=50)
    capacite = models.PositiveIntegerField(_('Capacité'))
    equipements = models.TextField(_('Équipements'), blank=True)
    batiment = models.CharField(_('Bâtiment'), max_length=50)
    etage = models.IntegerField(_('Étage'))

    class Meta:
        verbose_name = _('Salle')
        verbose_name_plural = _('Salles')
        ordering = ['batiment', 'etage', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.batiment} - {self.etage})"

class Cours(models.Model):
    """Modèle principal pour les cours"""
    formation = models.ForeignKey( Formation, on_delete=models.CASCADE, verbose_name=_('Formation'))
    formateur = models.ForeignKey( Formateur, on_delete=models.PROTECT, verbose_name=_('Formateur'))
    salle = models.ForeignKey( Salle, on_delete=models.PROTECT, verbose_name=_('Salle'), null=True, blank=True)
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    date = models.DateField(_('Date'))
    heure_debut = models.TimeField(_('Heure de début'))
    heure_fin = models.TimeField(_('Heure de fin'))
    objectifs = models.TextField(_('Objectifs pédagogiques'), blank=True)
    materiel_requis = models.TextField(_('Matériel requis'), blank=True)
    notes = models.TextField(_('Notes complémentaires'), blank=True)
    created_at = models.DateTimeField(_('Date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Dernière modification'), auto_now=True)

    class Meta:
        verbose_name = _('Cours')
        verbose_name_plural = _('Cours')
        ordering = ['date', 'heure_debut']
        constraints = [
            models.UniqueConstraint(
                fields=['salle', 'date', 'heure_debut'],
                name='unique_booking'
            ),
            models.UniqueConstraint(
                fields=['formateur', 'date', 'heure_debut'],
                name='unique_formateur_availability'
            )
        ]

    def __str__(self):
        return f"{self.titre} - {self.date} {self.heure_debut}"

    def get_absolute_url(self):
        return reverse('planning:cours_detail', args=[str(self.id)])

    @property
    def duree(self):
        """Calcule la durée du cours en heures"""
        delta = datetime.combine(self.date, self.heure_fin) - datetime.combine(self.date, self.heure_debut)
        return delta.total_seconds() / 3600

class Disponibilite(models.Model):
    """Modèle pour les disponibilités des formateurs"""
    formateur = models.ForeignKey( Formateur, on_delete=models.CASCADE, verbose_name=_('Formateur'))
    date_debut = models.DateTimeField(_('Date et heure de début'))
    date_fin = models.DateTimeField(_('Date et heure de fin'))
    notes = models.TextField(_('Notes'), blank=True)
    type = models.CharField( _('Type de disponibilité'), max_length=20,
                            choices=[
                                ('DISPONIBLE', _('Disponible')),
                                ('INDISPONIBLE', _('Indisponible')),
                                ],
                            default='DISPONIBLE')

    class Meta:
        verbose_name = _('Disponibilité')
        verbose_name_plural = _('Disponibilités')
        ordering = ['date_debut']

    def __str__(self):
        return f"{self.formateur} - {self.date_debut} à {self.date_fin}"