from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Q
from datetime import date

from .models import Cours, Salle, Disponibilite
from .forms import CoursForm, DisponibiliteForm

class PlanningMixin(LoginRequiredMixin):
    """Mixin de base pour les vues du planning"""
    
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'formateur'):
            return qs.filter(formateur=self.request.user.formateur)
        return qs

class CoursListView(PlanningMixin, ListView):
    model = Cours
    template_name = 'planning/cours_list.html'
    context_object_name = 'cours_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par date
        periode = self.request.GET.get('periode', 'futur')
        if periode == 'passe':
            queryset = queryset.filter(date__lt=date.today())
        elif periode == 'futur':
            queryset = queryset.filter(date__gte=date.today())
        
        # Filtrage par formation
        formation_id = self.request.GET.get('formation')
        if formation_id:
            queryset = queryset.filter(formation_id=formation_id)
        
        return queryset.order_by('date', 'heure_debut')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periode'] = self.request.GET.get('periode', 'futur')
        return context

class CoursDetailView(PlanningMixin, DetailView):
    model = Cours
    template_name = 'planning/cours_detail.html'

class CoursCreateView(PlanningMixin, CreateView):
    model = Cours
    form_class = CoursForm
    template_name = 'planning/cours_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'formateur'):
            kwargs['formateur'] = self.request.user.formateur
        return kwargs

    def form_valid(self, form):
        if hasattr(self.request.user, 'formateur'):
            form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Le cours a été créé avec succès."))
        return super().form_valid(form)

class CoursUpdateView(PlanningMixin, UpdateView):
    model = Cours
    form_class = CoursForm
    template_name = 'planning/cours_form.html'

    def form_valid(self, form):
        messages.success(self.request, _("Le cours a été mis à jour avec succès."))
        return super().form_valid(form)

class CoursDeleteView(PlanningMixin, DeleteView):
    model = Cours
    template_name = 'planning/cours_confirm_delete.html'
    success_url = reverse_lazy('planning:cours_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Le cours a été supprimé avec succès."))
        return super().delete(request, *args, **kwargs)

class DisponibiliteListView(PlanningMixin, ListView):
    model = Disponibilite
    template_name = 'planning/disponibilite_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            formateur=self.request.user.formateur,
            date_fin__gte=date.today()
        ).order_by('date_debut')

class DisponibiliteCreateView(PlanningMixin, CreateView):
    model = Disponibilite
    form_class = DisponibiliteForm
    template_name = 'planning/disponibilite_form.html'
    success_url = reverse_lazy('planning:disponibilite_list')

    def form_valid(self, form):
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Disponibilité enregistrée avec succès."))
        return super().form_valid(form)

class SalleListView(ListView):
    model = Salle
    template_name = 'planning/salle_list.html'
    context_object_name = 'salles'