from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import LoginView, LogoutView


from eleves.models import Eleve
from .forms import CustomUserCreationForm, EleveRegistrationForm, FormateurRegistrationForm
from .models import CustomUser

# Create your views here.


def register(request):
    """Vue principale pour l'inscription qui redirige vers le bon formulaire"""
    if request.user.is_authenticated:
        messages.info(request, _("Vous êtes déjà connecté."))
        return redirect('home')

    context = {
        'user_type': request.GET.get('type', '')
    }
    return render(request, 'accounts/register.html', context)


def register_eleve(request):

    if request.method == 'POST':
        form = EleveRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_eleve = True
            user.save()
        # Création du profil élève
        Eleve.objects.create(
            user=user,
            date_naissance=form.cleaned_data['date_naissance'],
            numero_etudiant=form.cleaned_data['numero_etudiant']
        )
        login(request, user)
        messages.success(
            request, f'Inscription réussie ! Bienvenue, {user.get_full_name()}')
        return redirect('eleve_dashboard')
    else:
        form = EleveRegistrationForm()
        return render(request, 'accounts/register_eleve.html', {'form': form})


def register_formateur(request):
    if request.method == 'POST':
        user_form = FormateurRegistrationForm(request.POST)
        formateur_form = FormateurRegistrationForm(request.POST, request.FILES)

        if user_form.is_valid() and formateur_form.is_valid():
            # Création de l'utilisateur
            user = user_form.save(commit=False)
            user.is_formateur = True
            user.save()

            # Création du profil formateur
            formateur = formateur_form.save(commit=False)
            formateur.user = user
            formateur.save()

            # Envoi d'email de confirmation
            from django.core.mail import send_mail
            send_mail(
                _("Confirmation d'inscription formateur"),
                _("Votre compte formateur a bien été créé."),
                'noreply@formation.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, _(
                "Inscription formateur réussie ! Votre compte est en attente de validation."))
            return redirect('login')
    else:
        user_form = FormateurRegistrationForm()
        formateur_form = FormateurRegistrationForm()

    return render(request, 'accounts/register_formateur.html', {
        'user_form': user_form,
        'formateur_form': formateur_form
    })


@login_required
def profile(request):
    user = request.user
    context = {'user': user}
    if user.is_eleve and hasattr(user, 'eleve'):
        context['profile'] = user.eleve
        context['profile_type'] = 'eleve'
    elif user.is_formateur and hasattr(user, 'formateur'):
        context['profile'] = user.formateur
        context['profile_type'] = 'formateur'
    return render(request, 'accounts/profile.html', context)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    extra_context = {'title': _('Connexion')}

    def get_success_url(self):
        user = self.request.user
        if user.is_formateur:
            return reverse_lazy('formateurs:dashboard')  # à définir
        elif user.is_eleve:
            return reverse_lazy('eleve_dashboard')  # à définir
        return reverse_lazy('accounts:profile')  # fallback


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("Vous avez été déconnecté avec succès."))
        return super().dispatch(request, *args, **kwargs)
