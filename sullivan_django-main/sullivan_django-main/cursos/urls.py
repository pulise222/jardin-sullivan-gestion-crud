from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CursoViewSet, estudiantes_del_curso

router = DefaultRouter()
router.register(r'', CursoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    path('<int:curso_id>/estudiantes/', estudiantes_del_curso)
]
