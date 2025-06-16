from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from formateurs.models import Formateur
from formations.models import Formation

def document_upload_path(instance, filename):
    """Chemin de stockage personnalisé pour les documents"""
    return f'documents/formateur_{instance.formateur.id}/{filename}'

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('PDF', 'PDF'),
        ('DOC', 'Document Word'),
        ('XLS', 'Tableur Excel'),
        ('PPT', 'Présentation'),
        ('IMG', 'Image'),
        ('VID', 'Vidéo'),
        ('AUD', 'Audio'),
        ('LINK', 'Lien externe'),
        ('OTHER', 'Autre'),
    ]

    formateur = models.ForeignKey(
        Formateur,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Formateur')
    )
    titre = models.CharField(
        _('Titre'),
        max_length=200,
        help_text=_("Titre descriptif du document")
    )
    fichier = models.FileField(
        _('Fichier'),
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator([
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 
                'ppt', 'pptx', 'jpg', 'jpeg', 'png',
                'mp4', 'mp3', 'avi', 'mov'
            ])
        ],
        blank=True,
        null=True,
        help_text=_("Fichier à uploader (max 20Mo)")
    )
    url = models.URLField(
        _('URL externe'),
        blank=True,
        null=True,
        help_text=_("Lien vers une ressource externe")
    )
    type_document = models.CharField(
        _('Type de document'),
        max_length=10,
        choices=DOCUMENT_TYPES,
        default='PDF'
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_("Description détaillée du contenu")
    )
    formations = models.ManyToManyField(
        Formation,
        related_name='documents',
        verbose_name=_('Formations associées'),
        blank=True,
        help_text=_("Formations pour lesquelles ce document est pertinent")
    )
    visible_eleves = models.BooleanField(
        _('Visible par les élèves'),
        default=True,
        help_text=_("Si ce document doit être visible par les élèves")
    )
    date_ajout = models.DateTimeField(
        _('Date d\'ajout'),
        auto_now_add=True
    )
    date_modification = models.DateTimeField(
        _('Dernière modification'),
        auto_now=True
    )
    tags = models.CharField(
        _('Mots-clés'),
        max_length=255,
        blank=True,
        help_text=_("Mots-clés séparés par des virgules pour faciliter la recherche")
    )

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-date_ajout']
        permissions = [
            ('can_share_document', _('Peut partager des documents avec les élèves')),
            ('can_manage_all_documents', _('Peut gérer tous les documents')),
        ]

    def __str__(self):
        return f"{self.titre} ({self.get_type_document_display()})"

    def get_absolute_url(self):
        return reverse('documents:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Détermine automatiquement le type de document"""
        if self.fichier:
            extension = self.fichier.name.split('.')[-1].lower()
            if extension in ['pdf']:
                self.type_document = 'PDF'
            elif extension in ['doc', 'docx']:
                self.type_document = 'DOC'
            elif extension in ['xls', 'xlsx']:
                self.type_document = 'XLS'
            elif extension in ['ppt', 'pptx']:
                self.type_document = 'PPT'
            elif extension in ['jpg', 'jpeg', 'png', 'gif']:
                self.type_document = 'IMG'
            elif extension in ['mp4', 'avi', 'mov']:
                self.type_document = 'VID'
            elif extension in ['mp3', 'wav']:
                self.type_document = 'AUD'
        elif self.url:
            self.type_document = 'LINK'
        
        super().save(*args, **kwargs)

    def get_icon_class(self):
        """Renvoie la classe Font Awesome correspondant au type de document"""
        icons = {
            'PDF': 'fa-file-pdf',
            'DOC': 'fa-file-word',
            'XLS': 'fa-file-excel',
            'PPT': 'fa-file-powerpoint',
            'IMG': 'fa-file-image',
            'VID': 'fa-file-video',
            'AUD': 'fa-file-audio',
            'LINK': 'fa-link',
            'OTHER': 'fa-file',
        }
        return icons.get(self.type_document, 'fa-file')

    def get_file_size(self):
        """Renvoie la taille du fichier formatée"""
        if self.fichier and self.fichier.size:
            size = self.fichier.size
            if size < 1024:
                return f"{size} octets"
            elif size < 1024 * 1024:
                return f"{round(size / 1024, 1)} Ko"
            else:
                return f"{round(size / (1024 * 1024), 1)} Mo"
        return None

    def is_accessible_by(self, user):
        """Vérifie si l'utilisateur a accès à ce document"""
        if hasattr(user, 'formateur') and user.formateur == self.formateur:
            return True
        if hasattr(user, 'eleve') and self.visible_eleves:
            if self.formations.exists():
                return user.eleve.inscription_set.filter(
                    formation__in=self.formations.all(),
                    statut='valide'
                ).exists()
            return True
        return False