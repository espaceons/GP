"""
URL configuration for gestion_formation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('formations.urls', namespace='formations')),
    path('comptes/', include('accounts.urls', namespace='accounts')),
    path('formateurs/', include('formateurs.urls', namespace='formateurs')),
    path('eleves/', include('eleves.urls', namespace='eleves')),
    path('planning/', include('planning.urls', namespace='planning')),
    path('presence/', include('presence.urls', namespace='presence')),
    path('documents/', include('documents.urls', namespace='documents')),
]
