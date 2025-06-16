from django.db import models

# Create your models here.
from accounts.models import CustomUser

class Formateur(models.Model):
    """
    Modèle représentant un formateur dans le système de gestion de formation.
    Un formateur est un utilisateur qui dispense des formations.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_formateur': True}, related_name='formateur')
    specialite = models.CharField(max_length=100, help_text="Spécialité du formateur.")
    experience = models.PositiveIntegerField(help_text="Années d'expérience du formateur.")
    bio = models.TextField()
    matricule = models.CharField( max_length=20, unique=True, help_text="Matricule unique du formateur.")

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - {self.specialite}"