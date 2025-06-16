from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Count, Q

from .models import Eleve, DocumentEleve
from .forms import EleveUpdateForm, DocumentEleveForm
from formations.models import Formation, Inscription
from presence.models import Presence

class EleveRequiredMixin(LoginRequiredMixin):
    """Vérifie que l'utilisateur est un élève"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'eleve'):
            messages.error(request, _("Accès réservé aux élèves"))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class DashboardView(EleveRequiredMixin, TemplateView):
    template_name = 'eleves/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eleve = self.request.user.eleve
        
        # Prochaines formations
        context['inscriptions'] = Inscription.objects.filter(
            eleve=eleve,
            statut='valide'
        ).select_related('formation')[:3]
        
        # Derniers documents
        context['documents'] = DocumentEleve.objects.filter(
            eleve=eleve
        ).order_by('-date_depot')[:5]
        
        # Statistiques de présence
        presences = Presence.objects.filter(eleve=eleve)
        context['presence_count'] = presences.count()
        context['presence_rate'] = round(
            presences.filter(present=True).count() / context['presence_count'] * 100, 1
        ) if context['presence_count'] > 0 else 0
        
        return context

class ProfilView(EleveRequiredMixin, DetailView):
    model = Eleve
    template_name = 'eleves/profil/detail.html'
    
    def get_object(self):
        return self.request.user.eleve

class ProfilUpdateView(EleveRequiredMixin, UpdateView):
    form_class = EleveUpdateForm
    template_name = 'eleves/profil/form.html'
    success_url = reverse_lazy('eleves:profil')
    
    def get_object(self):
        return self.request.user.eleve
    
    def form_valid(self, form):
        messages.success(self.request, _("Profil mis à jour avec succès"))
        return super().form_valid(form)

class MesFormationsListView(EleveRequiredMixin, ListView):
    model = Inscription
    template_name = 'eleves/formations/list.html'
    context_object_name = 'inscriptions'
    
    def get_queryset(self):
        return Inscription.objects.filter(
            eleve=self.request.user.eleve
        ).select_related('formation').order_by('-date_inscription')

class FormationDetailView(EleveRequiredMixin, DetailView):
    model = Formation
    template_name = 'eleves/formations/detail.html'
    context_object_name = 'formation'
    
    def get_queryset(self):
        return Formation.objects.filter(
            inscriptions__eleve=self.request.user.eleve
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscription'] = Inscription.objects.get(
            formation=self.object,
            eleve=self.request.user.eleve
        )
        return context

class MesDocumentsListView(EleveRequiredMixin, ListView):
    model = DocumentEleve
    template_name = 'eleves/documents/list.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        return DocumentEleve.objects.filter(
            eleve=self.request.user.eleve
        ).order_by('-date_depot')

class DocumentCreateView(EleveRequiredMixin, CreateView):
    model = DocumentEleve
    form_class = DocumentEleveForm
    template_name = 'eleves/documents/form.html'
    success_url = reverse_lazy('eleves:mes_documents')
    
    def form_valid(self, form):
        form.instance.eleve = self.request.user.eleve
        messages.success(self.request, _("Document ajouté avec succès"))
        return super().form_valid(form)

class DocumentDetailView(EleveRequiredMixin, DetailView):
    model = DocumentEleve
    template_name = 'eleves/documents/detail.html'
    
    def get_queryset(self):
        return DocumentEleve.objects.filter(
            eleve=self.request.user.eleve
        )

class MesPresencesListView(EleveRequiredMixin, ListView):
    model = Presence
    template_name = 'eleves/presences/list.html'
    context_object_name = 'presences'
    paginate_by = 10
    
    def get_queryset(self):
        return Presence.objects.filter(
            eleve=self.request.user.eleve
        ).select_related('cours', 'cours__formation').order_by('-cours__date')

class PresenceStatsView(EleveRequiredMixin, TemplateView):
    template_name = 'eleves/presences/statistiques.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eleve = self.request.user.eleve
        
        # Statistiques globales
        presences = Presence.objects.filter(eleve=eleve)
        total = presences.count()
        present = presences.filter(present=True).count()
        
        context['total'] = total
        context['present'] = present
        context['absent'] = total - present
        context['rate'] = round(present / total * 100, 1) if total > 0 else 0
        
        # Par formation
        formations_data = []
        for formation in Formation.objects.filter(inscriptions__eleve=eleve):
            p = Presence.objects.filter(
                eleve=eleve,
                cours__formation=formation
            )
            total_f = p.count()
            present_f = p.filter(present=True).count()
            
            formations_data.append({
                'formation': formation,
                'total': total_f,
                'present': present_f,
                'rate': round(present_f / total_f * 100, 1) if total_f > 0 else 0
            })
        
        context['formations_data'] = sorted(
            formations_data, 
            key=lambda x: x['rate'], 
            reverse=True
        )
        
        return context