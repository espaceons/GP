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
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclusions de vos applications avec leurs namespaces
    path('', include('formations.urls', namespace='formations')),
    path('comptes/', include('accounts.urls', namespace='accounts')),
    path('formateurs/', include('formateurs.urls', namespace='formateurs')),
    path('eleves/', include('eleves.urls', namespace='eleves')),
    path('planning/', include('planning.urls', namespace='planning')),
    path('presence/', include('presence.urls', namespace='presence')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('formations/', include('formations.urls', namespace='formations')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
