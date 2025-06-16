from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'formations'

urlpatterns = [
    # Formations
    path('', views.FormationListView.as_view(), name='list'),
    path('ajouter/', views.FormationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FormationDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.FormationUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.FormationDeleteView.as_view(), name='delete'),
    
    # Modules
    path('<int:formation_pk>/modules/ajouter/', views.ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/modifier/', views.ModuleUpdateView.as_view(), name='module_update'),
    path('modules/<int:pk>/supprimer/', views.ModuleDeleteView.as_view(), name='module_delete'),
    
    # Domaines (API/JSON)
#    path('domaines/', views.DomaineListView.as_view(), name='domaine_list'),
]