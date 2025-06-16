from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'planning'

urlpatterns = [
    # Cours
    path('cours/', views.CoursListView.as_view(), name='cours_list'),
    path('cours/ajouter/', views.CoursCreateView.as_view(), name='cours_create'),
    path('cours/<int:pk>/', views.CoursDetailView.as_view(), name='cours_detail'),
    path('cours/<int:pk>/modifier/', views.CoursUpdateView.as_view(), name='cours_update'),
    path('cours/<int:pk>/supprimer/', views.CoursDeleteView.as_view(), name='cours_delete'),
    
    # Disponibilités
    path('disponibilites/', views.DisponibiliteListView.as_view(), name='disponibilite_list'),
    path('disponibilites/ajouter/', views.DisponibiliteCreateView.as_view(), name='disponibilite_create'),
    
    # Salles
    path('salles/', views.SalleListView.as_view(), name='salle_list'),
    
    # Calendrier
    path('calendrier/', views.CalendrierView.as_view(), name='calendrier'),
]