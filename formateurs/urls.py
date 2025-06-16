from django.urls import path
from django.utils.translation import gettext_lazy as _
from formateurs import views

app_name = 'formateurs'

urlpatterns = [
     # Tableau de bord
    path('', views.DashboardView, name='dashboard'),
    
    # Gestion des cours
    path('cours/', views.CoursListView.as_view(), name='cours_list'),
    path('cours/ajouter/', views.CoursCreateView.as_view(), name='cours_create'),
    path('cours/<int:pk>/', views.CoursDetailView.as_view(), name='cours_detail'),
    path('cours/<int:pk>/modifier/', views.CoursUpdateView.as_view(), name='cours_update'),
    path('cours/<int:pk>/supprimer/', views.CoursDeleteView.as_view(), name='cours_delete'),
    
    
    # Gestion des disponibilités
    path('disponibilites/', views.DisponibiliteView.as_view(), name='disponibilites'),
    path('disponibilites/ajouter/', views.DisponibiliteCreateView.as_view(), name='disponibilite_create'),
    path('disponibilites/<int:pk>/supprimer/', views.DisponibiliteDeleteView.as_view(), name='disponibilite_delete'),
    
    
    # Gestion des élèves
    path('mes-eleves/', views.MesElevesListView.as_view(), name='mes_eleves'),
    path('mes-eleves/<int:pk>/', views.EleveDetailView.as_view(), name='eleve_detail'),
    
    
    # Documents et ressources
    path('documents/', views.DocumentListView.as_view(), name='documents'),
    path('documents/ajouter/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/supprimer/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Statistiques
    path('statistiques/', views.StatistiquesView.as_view(), name='statistiques'),
    
    
]