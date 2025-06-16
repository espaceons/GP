from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.translation import gettext_lazy as _
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register, name='register'),
    path('inscription/formateur/', views.register_formateur, name='register_formateur'),
    path('inscription/eleve/', views.register_eleve, name='register_eleve'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        extra_context={'title': _('Connexion')}
    ), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='accounts/logout.html',
        extra_context={'title': _('Déconnexion')}
    ), name='logout'),
    path('profil/', views.profile, name='profile'),
    path('mot-de-passe/reinitialisation/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        extra_context={'title': _('Réinitialisation du mot de passe')}
    ), name='password_reset'),
]