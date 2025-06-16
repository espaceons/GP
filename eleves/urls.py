from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'eleves'

urlpatterns = [
    
    # Tableau de bord élève
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Profil élève
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('profil/modifier/', views.ProfilUpdateView.as_view(), name='profil_update'),
    
    # Formations
    path('mes-formations/', views.MesFormationsListView.as_view(), name='mes_formations'),
    path('formation/<int:pk>/', views.FormationDetailView.as_view(), name='formation_detail'),
    
    # Documents
    path('mes-documents/', views.MesDocumentsListView.as_view(), name='mes_documents'),
    path('document/ajouter/', views.DocumentCreateView.as_view(), name='document_create'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    
    # Présences
    path('mes-presences/', views.MesPresencesListView.as_view(), name='mes_presences'),
    path('presences/statistiques/', views.PresenceStatsView.as_view(), name='presence_stats'),
]