from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
import datetime

from planning.models import Cours, Disponibilite
from eleves.models import Eleve
from documents.models import Document
from formations.models import Formation
from presence.models import Presence

class FormateurRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Vérifie que l'utilisateur est un formateur"""
    def test_func(self):
        return hasattr(self.request.user, 'formateur')

    def handle_no_permission(self):
        messages.error(self.request, _("Accès réservé aux formateurs"))
        return super().handle_no_permission()

# Dashboard
class DashboardView(FormateurRequiredMixin, TemplateView):
    template_name = 'formateurs/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.request.user.formateur
        
        # Cours à venir (7 prochains jours)
        today = timezone.now().date()
        seven_days = today + datetime.timedelta(days=7)
        context['upcoming_courses'] = Cours.objects.filter(
            formateur=formateur,
            date__range=[today, seven_days]
        ).order_by('date', 'heure_debut')
        
        # Statistiques
        context['total_courses'] = Cours.objects.filter(formateur=formateur).count()
        context['upcoming_count'] = context['upcoming_courses'].count()
        
        # Élèves suivis
        context['students_count'] = Eleve.objects.filter(
            inscription__formation__in=formateur.formations.all()
        ).distinct().count()
        
        # Taux de présence global
        total_presences = Presence.objects.filter(
            cours__formateur=formateur
        ).count()
        present_count = Presence.objects.filter(
            cours__formateur=formateur,
            present=True
        ).count()
        context['attendance_rate'] = round((present_count / total_presences * 100), 1) if total_presences > 0 else 0
        
        return context

# Cours
class CoursListView(FormateurRequiredMixin, ListView):
    model = Cours
    template_name = 'formateurs/cours/list.html'
    context_object_name = 'cours_list'
    paginate_by = 10

    def get_queryset(self):
        return Cours.objects.filter(
            formateur=self.request.user.formateur
        ).order_by('-date', 'heure_debut')

class CoursCreateView(FormateurRequiredMixin, CreateView):
    model = Cours
    fields = ['formation', 'titre', 'date', 'heure_debut', 'heure_fin', 'salle', 'objectifs', 'materiel']
    template_name = 'formateurs/cours/form.html'

    def form_valid(self, form):
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Cours créé avec succès"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('formateurs:cours_detail', kwargs={'pk': self.object.pk})

class CoursDetailView(FormateurRequiredMixin, DetailView):
    model = Cours
    template_name = 'formateurs/cours/detail.html'

    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)

class CoursUpdateView(FormateurRequiredMixin, UpdateView):
    model = Cours
    fields = ['formation', 'titre', 'date', 'heure_debut', 'heure_fin', 'salle', 'objectifs', 'materiel']
    template_name = 'formateurs/cours/form.html'

    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)

    def form_valid(self, form):
        messages.success(self.request, _("Cours mis à jour avec succès"))
        return super().form_valid(form)

class CoursDeleteView(FormateurRequiredMixin, DeleteView):
    model = Cours
    template_name = 'formateurs/cours/confirm_delete.html'
    success_url = reverse_lazy('formateurs:cours_list')

    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Cours supprimé avec succès"))
        return super().delete(request, *args, **kwargs)

# Disponibilités
class DisponibiliteView(FormateurRequiredMixin, ListView):
    model = Disponibilite
    template_name = 'formateurs/disponibilites/list.html'

    def get_queryset(self):
        return Disponibilite.objects.filter(
            formateur=self.request.user.formateur,
            date_fin__gte=timezone.now()
        ).order_by('date_debut')

class DisponibiliteCreateView(FormateurRequiredMixin, CreateView):
    model = Disponibilite
    fields = ['date_debut', 'date_fin', 'type', 'notes']
    template_name = 'formateurs/disponibilites/form.html'
    success_url = reverse_lazy('formateurs:disponibilites')

    def form_valid(self, form):
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Disponibilité enregistrée avec succès"))
        return super().form_valid(form)

class DisponibiliteDeleteView(FormateurRequiredMixin, DeleteView):
    model = Disponibilite
    template_name = 'formateurs/disponibilites/confirm_delete.html'
    success_url = reverse_lazy('formateurs:disponibilites')

    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Disponibilité supprimée avec succès"))
        return super().delete(request, *args, **kwargs)

# Élèves
class MesElevesListView(FormateurRequiredMixin, ListView):
    template_name = 'formateurs/eleves/list.html'
    context_object_name = 'eleves'

    def get_queryset(self):
        formateur = self.request.user.formateur
        return Eleve.objects.filter(
            inscription__formation__in=formateur.formations.all()
        ).distinct().annotate(
            course_count=Count('presence', filter=Q(presence__cours__formateur=formateur)))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formations'] = self.request.user.formateur.formations.all()
        return context

class EleveDetailView(FormateurRequiredMixin, DetailView):
    model = Eleve
    template_name = 'formateurs/eleves/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.request.user.formateur
        eleve = self.object
        
        # Formations suivies par l'élève avec ce formateur
        context['inscriptions'] = Inscription.objects.filter(
            eleve=eleve,
            formation__in=formateur.formations.all()
        ).select_related('formation')
        
        # Présences aux cours
        context['presences'] = Presence.objects.filter(
            eleve=eleve,
            cours__formateur=formateur
        ).select_related('cours', 'cours__formation')
        
        # Calcul du taux de présence
        total = context['presences'].count()
        present = context['presences'].filter(present=True).count()
        context['attendance_rate'] = round((present / total * 100), 1) if total > 0 else 0
        
        return context

# Documents
class DocumentListView(FormateurRequiredMixin, ListView):
    model = Document
    template_name = 'formateurs/documents/list.html'
    
    def get_queryset(self):
        return Document.objects.filter(
            formateur=self.request.user.formateur
        ).order_by('-date_ajout')

class DocumentCreateView(FormateurRequiredMixin, CreateView):
    model = Document
    fields = ['titre', 'fichier', 'description', 'formations', 'visible_eleves']
    template_name = 'formateurs/documents/form.html'
    
    def form_valid(self, form):
        form.instance.formateur = self.request.user.formateur
        messages.success(self.request, _("Document ajouté avec succès"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('formateurs:document_detail', kwargs={'pk': self.object.pk})

class DocumentDetailView(FormateurRequiredMixin, DetailView):
    model = Document
    template_name = 'formateurs/documents/detail.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)

class DocumentDeleteView(FormateurRequiredMixin, DeleteView):
    model = Document
    template_name = 'formateurs/documents/confirm_delete.html'
    success_url = reverse_lazy('formateurs:documents')
    
    def get_queryset(self):
        return super().get_queryset().filter(formateur=self.request.user.formateur)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Document supprimé avec succès"))
        return super().delete(request, *args, **kwargs)

# Statistiques
class StatistiquesView(FormateurRequiredMixin, TemplateView):
    template_name = 'formateurs/statistiques.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formateur = self.request.user.formateur
        
        # Statistiques générales
        context['total_formations'] = formateur.formations.count()
        context['total_cours'] = Cours.objects.filter(formateur=formateur).count()
        context['total_eleves'] = Eleve.objects.filter(
            inscription__formation__in=formateur.formations.all()
        ).distinct().count()
        
        # Taux de présence par formation
        formations_data = []
        for formation in formateur.formations.all():
            presences = Presence.objects.filter(
                cours__formation=formation,
                cours__formateur=formateur
            )
            total = presences.count()
            present = presences.filter(present=True).count()
            rate = round((present / total * 100), 1) if total > 0 else 0
            
            formations_data.append({
                'formation': formation,
                'total': total,
                'present': present,
                'rate': rate
            })
        
        context['formations_data'] = sorted(
            formations_data, 
            key=lambda x: x['rate'], 
            reverse=True
        )
        
        # Évolution mensuelle
        current_year = timezone.now().year
        monthly_data = []
        for month in range(1, 13):
            month_start = timezone.datetime(current_year, month, 1)
            month_end = timezone.datetime(
                current_year, 
                month+1 if month < 12 else 12, 
                1 if month < 12 else 31
            )
            
            cours_count = Cours.objects.filter(
                formateur=formateur,
                date__range=[month_start, month_end]
            ).count()
            
            monthly_data.append({
                'month': month_start.strftime('%B'),
                'count': cours_count
            })
        
        context['monthly_data'] = monthly_data
        
        return context