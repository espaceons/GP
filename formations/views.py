from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Formation, Domaine, Module
from .forms import FormationForm, ModuleForm

class FormationListView(ListView):
    model = Formation
    template_name = 'formations/formation_list.html'
    context_object_name = 'formations'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par domaine
        domaine_id = self.request.GET.get('domaine')
        if domaine_id:
            queryset = queryset.filter(domaine_id=domaine_id)
        
        # Filtre actif/inactif
        actif = self.request.GET.get('actif')
        if actif in ['true', 'false']:
            queryset = queryset.filter(actif=actif == 'true')
        
        return queryset.select_related('domaine').prefetch_related('modules')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domaines'] = Domaine.objects.all()
        return context

class FormationDetailView(DetailView):
    model = Formation
    template_name = 'formations/formation_detail.html'
    context_object_name = 'formation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_form'] = ModuleForm(initial={'formation': self.object})
        return context

class FormationCreateView(PermissionRequiredMixin, CreateView):
    model = Formation
    form_class = FormationForm
    template_name = 'formations/formation_form.html'
    permission_required = 'formations.add_formation'
    success_url = reverse_lazy('formations:list')

    def form_valid(self, form):
        messages.success(self.request, _("Formation créée avec succès"))
        return super().form_valid(form)

class FormationUpdateView(PermissionRequiredMixin, UpdateView):
    model = Formation
    form_class = FormationForm
    template_name = 'formations/formation_form.html'
    permission_required = 'formations.change_formation'

    def form_valid(self, form):
        messages.success(self.request, _("Formation mise à jour avec succès"))
        return super().form_valid(form)

class FormationDeleteView(PermissionRequiredMixin, DeleteView):
    model = Formation
    template_name = 'formations/formation_confirm_delete.html'
    permission_required = 'formations.delete_formation'
    success_url = reverse_lazy('formations:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Formation supprimée avec succès"))
        return super().delete(request, *args, **kwargs)

class ModuleCreateView(PermissionRequiredMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'formations/module_form.html'
    permission_required = 'formations.add_module'

    def get_success_url(self):
        return reverse('formations:detail', kwargs={'pk': self.object.formation.pk})

    def form_valid(self, form):
        messages.success(self.request, _("Module ajouté avec succès"))
        return super().form_valid(form)

class ModuleUpdateView(PermissionRequiredMixin, UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'formations/module_form.html'
    permission_required = 'formations.change_module'

    def get_success_url(self):
        return reverse('formations:detail', kwargs={'pk': self.object.formation.pk})

    def form_valid(self, form):
        messages.success(self.request, _("Module modifié avec succès"))
        return super().form_valid(form)

class ModuleDeleteView(PermissionRequiredMixin, DeleteView):
    model = Module
    template_name = 'formations/module_confirm_delete.html'
    permission_required = 'formations.delete_module'

    def get_success_url(self):
        return reverse('formations:detail', kwargs={'pk': self.object.formation.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Module supprimé avec succès"))
        return super().delete(request, *args, **kwargs)