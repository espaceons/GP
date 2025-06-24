# Importez le formulaire de l'app documents
from datetime import datetime, timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q

# Importez tous les modèles nécessaires
# Assurez-vous d'avoir Inscription ici aussi
from documents.forms import DocumentForm
from eleves.models import Eleve, SuiviPedagogique, DocumentEleve, Inscription
# Pour les relations avec les élèves et les documents
from planning.models import Cours, Formation
# Pour la gestion des documents du formateur
from documents.models import Document
from presence.models import Presence

# Mixin personnalisé pour restreindre l'accès aux formateurs (réutilisé de documents-views ou planning-views)


class FormateurRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin pour restreindre l'accès aux vues aux utilisateurs qui sont des formateurs.
    """

    def test_func(self):
        # Vérifie si l'utilisateur est authentifié et a un profil de formateur
        return self.request.user.is_authenticated and hasattr(self.request.user, 'formateur')

    def handle_no_permission(self):
        # Redirige vers une page d'accès refusé ou affiche un message d'erreur
        # Assurez-vous que 'accueil' est une URL valide dans votre projet principal urls.py
        messages.error(self.request, _("Accès réservé aux formateurs."))
        return redirect('accueil')


# Vues pour le tableau de bord du formateur (maintenant une Class-Based View)
class DashboardView(FormateurRequiredMixin, TemplateView):
    template_name = 'formateurs/dashboard.html'  # Le même template HTML

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formateur = self.request.user.formateur

        # Cours à venir (7 prochains jours)
        today = timezone.now().date()
        seven_days = today + datetime.timedelta(days=7)
        upcoming_courses = Cours.objects.filter(
            formateur=formateur,
            date__range=[today, seven_days]
        ).order_by('date', 'heure_debut')

        # Cours passés non complétés (présences)
        incomplete_courses = Cours.objects.filter(
            formateur=formateur,
            date__lt=today,
            # Cela suppose qu'un cours est "incomplet" s'il n'a AUCUN enregistrement de présence.
            # Si la logique est plus complexe (ex: vérifier si tous les élèves n'ont pas été marqués),
            # elle nécessitera une requête plus sophistiquée.
            presence__isnull=True
        ).distinct()

        # Statistiques
        total_courses = Cours.objects.filter(formateur=formateur).count()
        upcoming_count = upcoming_courses.count()

        # Élèves suivis - Requête Corrigée
        # Filtre les élèves qui sont inscrits à des Formations ayant des Cours dispensés par ce Formateur.
        students = Eleve.objects.filter(
            inscription__formation__cours__formateur=formateur
        ).distinct().annotate(
            # Compte les enregistrements de Présence pour les cours de ce formateur spécifiques à l'élève
            course_count=Count('presence', filter=Q(
                presence__cours__formateur=formateur))
        )

        # Prochain cours (pour la carte en haut)
        next_course = upcoming_courses.first()

        # Taux de présence global
        total_presences = Presence.objects.filter(
            cours__formateur=formateur
        ).count()
        present_count = Presence.objects.filter(
            cours__formateur=formateur,
            present=True
        ).count()

        attendance_rate = (present_count / total_presences *
                           100) if total_presences > 0 else 0

        context.update({
            'upcoming_courses': upcoming_courses,
            'incomplete_courses': incomplete_courses,
            'next_course': next_course,
            'total_courses': total_courses,
            'upcoming_count': upcoming_count,
            'students': students[:5],  # 5 premiers seulement
            'attendance_rate': round(attendance_rate, 1),
            'today': today,
        })

        return context

# --- Vues pour la Gestion des Élèves (Mes Eleves) ---


class MesElevesListView(FormateurRequiredMixin, ListView):
    model = Eleve
    template_name = 'formateurs/mes_eleves_list.html'  # Créez ce template
    context_object_name = 'eleves_list'
    paginate_by = 10

    def get_queryset(self):
        """
        Retourne les élèves qui sont inscrits à des formations où le formateur connecté
        dispense des cours.
        """
        formateur = self.request.user.formateur
        # Cette requête est similaire à celle du tableau de bord
        return Eleve.objects.filter(
            inscription__formation__cours__formateur=formateur
        ).distinct().order_by('user__last_name', 'user__first_name')


class EleveDetailView(FormateurRequiredMixin, DetailView):
    model = Eleve
    template_name = 'formateurs/eleve_detail.html'  # Créez ce template
    context_object_name = 'eleve'

    def get_queryset(self):
        """
        S'assure que le formateur ne peut voir les détails que de ses propres élèves (ceux de ses formations).
        """
        formateur = self.request.user.formateur
        return Eleve.objects.filter(
            inscription__formation__cours__formateur=formateur,
            # Filtre aussi par PK pour s'assurer que c'est le bon élève
            pk=self.kwargs['pk']
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eleve = self.get_object()
        formateur = self.request.user.formateur

        # Récupérer les inscriptions de l'élève pour les formations du formateur
        context['inscriptions_du_formateur'] = Inscription.objects.filter(
            eleve=eleve,
            formation__cours__formateur=formateur
        ).distinct()

        # Récupérer les suivis pédagogiques de cet élève par ce formateur
        context['suivis_pedagogiques'] = SuiviPedagogique.objects.filter(
            eleve=eleve,
            formateur=formateur
        ).order_by('-date_entretien')

        # Récupérer les documents de cet élève qui sont visibles pour le formateur
        # Note: DocumentEleve est un modèle de l'app 'eleves', et non 'documents'.
        context['documents_eleve'] = DocumentEleve.objects.filter(eleve=eleve)

        return context


# --- Vues pour la Gestion des Documents (spécifiques au formateur) ---
# Ces vues gèrent le modèle Document de l'application 'documents', mais sont accessibles via 'formateurs'
# Assurez-vous que vous avez un `documents/forms.py` avec `DocumentForm`


class DocumentListView(FormateurRequiredMixin, ListView):
    model = Document
    template_name = 'formateurs/document_list.html'  # Créez ce template
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        """
        Retourne uniquement les documents associés au formateur connecté.
        Permet aux super-utilisateurs/staff de voir tous les documents.
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all().order_by('-date_ajout')
        return Document.objects.filter(formateur=self.request.user.formateur).order_by('-date_ajout')


class DocumentCreateView(FormateurRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'formateurs/document_form.html'  # Créez ce template
    # Redirige vers la liste des documents du formateur
    success_url = reverse_lazy('formateurs:documents')

    def form_valid(self, form):
        """
        Associe automatiquement le document au formateur connecté avant de sauvegarder.
        """
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _(
            "Le document a été ajouté avec succès !"))
        return super().form_valid(form)


class DocumentDetailView(FormateurRequiredMixin, DetailView):
    model = Document
    template_name = 'formateurs/document_detail.html'  # Créez ce template
    context_object_name = 'document'

    def get_queryset(self):
        """
        S'assure que le formateur ne peut voir que ses propres documents (ou tous s'il est admin/staff).
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(formateur=self.request.user.formateur)


class DocumentDeleteView(FormateurRequiredMixin, DeleteView):
    model = Document
    template_name = 'formateurs/document_confirm_delete.html'  # Créez ce template
    # Redirige après suppression
    success_url = reverse_lazy('formateurs:documents')

    def get_queryset(self):
        """
        S'assure que le formateur ne peut supprimer que ses propres documents (ou tous s'il est admin/staff).
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(formateur=self.request.user.formateur)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _(
            "Le document a été supprimé avec succès !"))
        return super().delete(request, *args, **kwargs)


# --- Vue pour les Statistiques (Ébauche) ---
class StatistiquesView(FormateurRequiredMixin, TemplateView):
    template_name = 'formateurs/statistiques.html'  # Créez ce template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.request.user.formateur

        # Exemple: Récupération de données pour les statistiques
        # Vous devrez ajouter ici la logique de calcul de vos statistiques
        # Exemples:
        # total_cours_termines = Cours.objects.filter(formateur=formateur, date__lt=timezone.now().date()).count()
        # total_eleves = Eleve.objects.filter(
        #     inscription__formation__cours__formateur=formateur
        # ).distinct().count()
        # presence_moyenne_par_cours = ...

        context['formateur'] = formateur
        context['message_statistiques'] = _(
            "Cette page affichera des statistiques détaillées pour vos cours et élèves. Veuillez implémenter la logique ici.")

        return context
