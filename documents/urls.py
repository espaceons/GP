from django.urls import path
from . import views

# Définir app_name au début du fichier (identique au namespace)
app_name = 'documents'  # Nom de votre application

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='list'),
    path('ajouter/', views.DocumentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='detail'),
    # ... autres paths
]