# Generated by Django 5.2.3 on 2025-06-24 14:36

import django.core.validators
import django.db.models.deletion
import documents.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('formateurs', '0001_initial'),
        ('formations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre descriptif du document', max_length=200, verbose_name='Titre')),
                ('fichier', models.FileField(blank=True, help_text='Fichier à uploader (max 20Mo)', null=True, upload_to=documents.models.document_upload_path, validators=[django.core.validators.FileExtensionValidator(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'mp4', 'mp3', 'avi', 'mov'])], verbose_name='Fichier')),
                ('url', models.URLField(blank=True, help_text='Lien vers une ressource externe', null=True, verbose_name='URL externe')),
                ('type_document', models.CharField(choices=[('PDF', 'PDF'), ('DOC', 'Document Word'), ('XLS', 'Tableur Excel'), ('PPT', 'Présentation'), ('IMG', 'Image'), ('VID', 'Vidéo'), ('AUD', 'Audio'), ('LINK', 'Lien externe'), ('OTHER', 'Autre')], default='PDF', max_length=10, verbose_name='Type de document')),
                ('description', models.TextField(blank=True, help_text='Description détaillée du contenu', verbose_name='Description')),
                ('visible_eleves', models.BooleanField(default=True, help_text='Si ce document doit être visible par les élèves', verbose_name='Visible par les élèves')),
                ('date_ajout', models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
                ('tags', models.CharField(blank=True, help_text='Mots-clés séparés par des virgules pour faciliter la recherche', max_length=255, verbose_name='Mots-clés')),
                ('formateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='formateurs.formateur', verbose_name='Formateur')),
                ('formations', models.ManyToManyField(blank=True, help_text='Formations pour lesquelles ce document est pertinent', related_name='documents', to='formations.formation', verbose_name='Formations associées')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'ordering': ['-date_ajout'],
                'permissions': [('can_share_document', 'Peut partager des documents avec les élèves'), ('can_manage_all_documents', 'Peut gérer tous les documents')],
            },
        ),
    ]
