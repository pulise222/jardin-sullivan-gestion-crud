# academico/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('boletin/curso/<int:curso_id>/periodo/<int:periodo_id>/', views.boletin_curso_json),
    path('boletin/curso/<int:curso_id>/periodo/<int:periodo_id>/pdf/', views.boletin_curso_pdf),
    path('contexto/', views.contexto_academico),
]