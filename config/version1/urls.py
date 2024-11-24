# version1/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.televersement, name='home'),  
    path('telechargement/', views.telechargement, name='telechargement'),
]
