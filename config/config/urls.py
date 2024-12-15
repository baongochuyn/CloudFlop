"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from version1 import views
from django.conf.urls.static import static

urlpatterns = [
    path('', lambda request: redirect('/version1/', permanent=False)),

    path('admin/', admin.site.urls),
    path('version1/', include('version1.urls')),  # Incluez version1
    path('version2/', include('version2.urls')),  # Incluez version1

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ajouter les fichiers médias pendant le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
