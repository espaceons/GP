from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    This allows for additional fields and customization in the future.
    """
    is_eleve = models.BooleanField(default=False, help_text="Indique si l'utilisateur est un eleve.")
    is_formateur = models.BooleanField(default=False, help_text="Indique si l'utilisateur est un formateur.")
    telephone = models.CharField(max_length=15, blank=True, null=True, help_text="Numéro de téléphone de l'utilisateur.")
    adresse = models.CharField(max_length=255, blank=True, null=True, help_text="Adresse de l'utilisateur.")
    email = models.EmailField(unique=True, help_text="Adresse e-mail de l'utilisateur.")
    # You can add additional fields here if needed
    # For example:
    # bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.get_full_name() or self.username