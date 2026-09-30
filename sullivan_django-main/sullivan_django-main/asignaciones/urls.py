# asignaciones/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CursoProfesorMateriaViewSet

router = DefaultRouter()
# Como este include irá bajo /asignaciones/, aquí usamos prefijo vacío
router.register(r'', CursoProfesorMateriaViewSet, basename='asignaciones')

urlpatterns = [
    path('', include(router.urls)),
]
