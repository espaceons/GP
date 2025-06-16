from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'presence'

urlpatterns = [
    path('marquer/<int:pk>/', views.MarquerPresenceView.as_view(), name='marquer'),
    path('mes-presences/', views.PresenceListView.as_view(), name='mes_presences'),
    path('formateur/', views.PresenceFormateurListView.as_view(), name='formateur_list'),
    path('statistiques/', views.StatistiquesPresenceView.as_view(), name='statistiques'),
]