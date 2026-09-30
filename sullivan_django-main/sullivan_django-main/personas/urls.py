from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonaViewSet, 
    persona_me, 
    listar_cursos_profesor, 
    asignar_curso_materia_profesor, 
    eliminar_curso_profesor, 
    buscar_personas,
    persona_avatar,
    )

router = DefaultRouter()
router.register(r'', PersonaViewSet, basename='personas')


urlpatterns = [
    path('me/', persona_me, name='persona-me'),
    path('<int:persona_id>/cursos-materias/', listar_cursos_profesor, name='listar-cursos-profesor'),
    path('<int:persona_id>/cursos/<int:curso_id>/materias/<int:materia_id>/', asignar_curso_materia_profesor, name='asignar-curso-materia-profesor'),
    path('<int:persona_id>/cursos/<int:curso_id>/materias/<int:materia_id>/eliminar/', eliminar_curso_profesor, name='eliminar-curso-profesor'),
    path('buscar/', buscar_personas, name='buscar-personas'),
    path('<int:persona_id>/avatar/', persona_avatar),
    path('', include(router.urls)),
]
