from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Document
from .forms import DocumentForm
from formateurs.models import Formateur # Assurez-vous d'importer Formateur pour les checks

# Mixin personnalisé pour restreindre l'accès aux formateurs
class FormateurRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin pour restreindre l'accès aux vues aux utilisateurs qui sont des formateurs.
    """
    def test_func(self):
        # Vérifie si l'utilisateur est authentifié et a un profil de formateur
        return self.request.user.is_authenticated and hasattr(self.request.user, 'formateur')

    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission d'accéder à cette page."))
        return redirect(reverse_lazy('accueil')) # Redirige vers une page d'accueil ou d'accès refusé


# Vues pour le modèle Document
class DocumentListView(FormateurRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html' # Créez ce template
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        """
        Retourne uniquement les documents associés au formateur connecté.
        Les super-utilisateurs et staff peuvent voir tous les documents.
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all().order_by('-date_ajout')
        return Document.objects.filter(formateur=self.request.user.formateur).order_by('-date_ajout')


class DocumentDetailView(FormateurRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html' # Créez ce template
    context_object_name = 'document'

    def get_queryset(self):
        """
        S'assure que le formateur ne peut voir que ses propres documents (ou tous s'il est admin/staff).
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(formateur=self.request.user.formateur)


class DocumentCreateView(FormateurRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html' # Créez ce template
    success_url = reverse_lazy('documents:list') # Redirige vers la liste des documents après succès

    def form_valid(self, form):
        """
        Associe automatiquement le document au formateur connecté avant de sauvegarder.
        """
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Le document a été ajouté avec succès !"))
        return super().form_valid(form)


class DocumentUpdateView(FormateurRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    
    def get_queryset(self):
        """
        S'assure que le formateur ne peut modifier que ses propres documents (ou tous s'il est admin/staff).
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(formateur=self.request.user.formateur)

    def get_success_url(self):
        messages.success(self.request, _("Le document a été mis à jour avec succès !"))
        return reverse_lazy('documents:detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(FormateurRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html' # Créez ce template
    success_url = reverse_lazy('documents:list')

    def get_queryset(self):
        """
        S'assure que le formateur ne peut supprimer que ses propres documents (ou tous s'il est admin/staff).
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(formateur=self.request.user.formateur)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Le document a été supprimé avec succès !"))
        return super().delete(request, *args, **kwargs)

