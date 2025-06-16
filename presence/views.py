from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import HttpResponseForbidden

from planning.models import Cours
from .models import Presence
from .forms import PresenceForm, BulkPresenceForm

class MarquerPresenceView(LoginRequiredMixin, UpdateView):
    """Vue pour marquer les présences d'un cours"""
    model = Cours
    template_name = 'presence/marquer_presence.html'
    form_class = BulkPresenceForm
    context_object_name = 'cours'

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'formateur'):
            return qs.filter(formateur=self.request.user.formateur)
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eleves'] = self.object.formation.inscription_set.filter(
            statut='valide'
        ).select_related('eleve__user')
        return context

    def form_valid(self, form):
        # Enregistrement des présences
        for eleve in self.get_context_data()['eleves']:
            presence, created = Presence.objects.get_or_create(
                cours=self.object,
                eleve=eleve.eleve,
                defaults={'present': form.cleaned_data[f'presence_{eleve.eleve.id}']}
            )
            if not created:
                presence.present = form.cleaned_data[f'presence_{eleve.eleve.id}']
                presence.save()

        messages.success(self.request, _("Les présences ont été enregistrées avec succès."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('planning:cours_detail', kwargs={'pk': self.object.pk})

class PresenceListView(LoginRequiredMixin, ListView):
    """Vue pour lister les présences d'un élève"""
    model = Presence
    template_name = 'presence/presence_list.html'
    context_object_name = 'presences'

    def get_queryset(self):
        if hasattr(self.request.user, 'eleve'):
            return super().get_queryset().filter(
                eleve=self.request.user.eleve
            ).select_related('cours__formation', 'cours__formateur')
        return super().get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'eleve'):
            context['eleve'] = self.request.user.eleve
            context['taux_presence'] = self.calculate_attendance_rate()
        return context

    def calculate_attendance_rate(self):
        total = self.get_queryset().count()
        if total == 0:
            return 0
        present = self.get_queryset().filter(present=True).count()
        return round((present / total) * 100, 1)

class PresenceFormateurListView(LoginRequiredMixin, ListView):
    """Vue pour lister les présences par cours (formateur)"""
    model = Presence
    template_name = 'presence/presence_formateur_list.html'

    def get_queryset(self):
        if hasattr(self.request.user, 'formateur'):
            return Presence.objects.filter(
                cours__formateur=self.request.user.formateur
            ).select_related(
                'cours', 'eleve__user', 'cours__formation'
            ).order_by('-cours__date', 'eleve__user__last_name')
        return super().get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'formateur'):
            context['cours_list'] = Cours.objects.filter(
                formateur=self.request.user.formateur
            ).distinct()
        return context