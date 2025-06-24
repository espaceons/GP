from datetime import date
from django.db import models
from django.conf import settings  # Importe les paramètres de Django
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator
from formations.models import Formation
import uuid


class Eleve(models.Model):
    """
    Modèle représentant un élève/étudiant dans le système
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE,
                                related_name='eleve', verbose_name=_('Compte utilisateur'))

    # Identifiants scolaires
    numero_etudiant = models.CharField(_('Numéro étudiant'), max_length=20, unique=True, default=uuid.uuid4(
    ).hex[:8].upper(), help_text=_('Identifiant unique de l\'étudiant'))

    # Informations personnelles
    date_naissance = models.DateField(
        _('Date de naissance'), null=True, blank=True)
    telephone = models.CharField(_('Téléphone'), max_length=20,
                                 validators=[
        RegexValidator(
            regex=r'^\+?[0-9]{9,15}$',
            message=_("Format de téléphone invalide")
        )
    ],
        blank=True,
        null=True
    )
    adresse = models.TextField(_('Adresse'), blank=True, null=True)
    ville = models.CharField(_('Ville'), max_length=100, blank=True, null=True)
    code_postal = models.CharField(
        _('Code postal'), max_length=10, blank=True, null=True)
    pays = models.CharField(_('Pays'), max_length=100,
                            default='France', blank=True,  null=True)

    # Relations
    formations = models.ManyToManyField(
        Formation,  through='Inscription', related_name='eleves',  verbose_name=_('Formations suivies'))

    # Métadonnées
    created_at = models.DateTimeField(
        _('Date d\'inscription'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Dernière mise à jour'), auto_now=True)

    class Meta:
        verbose_name = _('Élève')
        verbose_name_plural = _('Élèves')
        ordering = ['user__last_name', 'user__first_name']
        permissions = [
            ('can_view_dashboard', _('Peut accéder au tableau de bord élève')),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.numero_etudiant})"

    def get_absolute_url(self):
        return reverse('eleves:detail', kwargs={'pk': self.pk})

    @property
    def email(self):
        return self.user.email

    @property
    def nom_complet(self):
        return self.user.get_full_name()

    def get_age(self):
        """Calcule l'âge de l'élève"""
        if not self.date_naissance:
            return None
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (
                self.date_naissance.month, self.date_naissance.day)
        )


class Inscription(models.Model):
    """
    Modèle pour gérer les inscriptions aux formations
    """
    STATUT_CHOICES = [
        ('en_attente', _('En attente')),
        ('valide', _('Validée')),
        ('refuse', _('Refusée')),
        ('abandon', _('Abandon')),
        ('termine', _('Terminée')),
    ]

    eleve = models.ForeignKey(Eleve,  on_delete=models.CASCADE,
                              related_name='inscriptions', verbose_name=_('Élève'))
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE,
                                  related_name='inscriptions', verbose_name=_('Formation'))
    date_inscription = models.DateTimeField(
        _('Date d\'inscription'),  auto_now_add=True)
    date_debut = models.DateField(_('Date de début'),  null=True, blank=True)
    date_fin = models.DateField(_('Date de fin'),  null=True, blank=True)
    statut = models.CharField(
        _('Statut'),  max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes = models.TextField(_('Notes administratives'), blank=True, null=True)

    class Meta:
        verbose_name = _('Inscription')
        verbose_name_plural = _('Inscriptions')
        unique_together = ('eleve', 'formation')
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.eleve} - {self.formation} ({self.get_statut_display()})"

    def get_duree(self):
        """Calcule la durée de la formation en jours"""
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days
        return None

    def is_active(self):
        """Vérifie si l'inscription est active"""
        return self.statut in ['valide', 'termine']


class SuiviPedagogique(models.Model):
    """
    Modèle pour le suivi pédagogique des élèves
    """
    eleve = models.ForeignKey(Eleve,  on_delete=models.CASCADE,
                              related_name='suivis',  verbose_name=_('Élève'))
    formateur = models.ForeignKey('formateurs.Formateur',  on_delete=models.SET_NULL,
                                  null=True,  blank=True,  verbose_name=_('Référent pédagogique'))
    date_entretien = models.DateTimeField(
        _('Date de l\'entretien'),  auto_now_add=True)
    notes = models.TextField(_('Notes pédagogiques'))
    objectifs = models.TextField(
        _('Objectifs pédagogiques'),  blank=True,  null=True)
    evaluation = models.TextField(_('Évaluation'),  blank=True,  null=True)

    class Meta:
        verbose_name = _('Suivi pédagogique')
        verbose_name_plural = _('Suivis pédagogiques')
        ordering = ['-date_entretien']

    def __str__(self):
        return f"Suivi de {self.eleve} par {self.formateur}"


class DocumentEleve(models.Model):
    """
    Modèle pour les documents spécifiques à un élève
    (CV, lettre de motivation, etc.)
    """
    eleve = models.ForeignKey(Eleve,  on_delete=models.CASCADE,
                              related_name='documents', verbose_name=_('Élève'))
    type_document = models.CharField(_('Type de document'), max_length=50,  choices=[
        ('cv', _('CV')),
        ('lm', _('Lettre de motivation')),
        ('diplome', _('Diplôme')),
        ('autre', _('Autre')),
    ]
    )
    fichier = models.FileField(_('Fichier'),  upload_to='eleves/documents/')
    date_depot = models.DateTimeField(_('Date de dépôt'),  auto_now_add=True)
    valide = models.BooleanField(_('Validé'),  default=False)

    class Meta:
        verbose_name = _('Document élève')
        verbose_name_plural = _('Documents élèves')

    def __str__(self):
        return f"{self.get_type_document_display()} - {self.eleve}"
