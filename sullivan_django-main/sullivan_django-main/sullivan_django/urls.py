"""
================================================================================
ENRUTADOR PRINCIPAL (URLCONF) - PROYECTO SULLIVAN
================================================================================
Este archivo es el "índice telefónico" o mapa de rutas de todo el Backend.
Cuando un cliente (como nuestra app de React o un navegador) hace una petición HTTP:
  1. Django recibe la URL solicitada (ejemplo: 'http://127.0.0.1:8000/estudiantes/').
  2. Django recorre la lista `urlpatterns` de arriba a abajo.
  3. En la primera coincidencia que encuentra, delega la petición a la vista
     correspondiente o al archivo `urls.py` de la sub-aplicación (usando `include`).
================================================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Vistas de autenticación JWT estándar de SimpleJWT:
# - TokenObtainPairView: Recibe 'username' y 'password' -> Retorna { access, refresh }
# - TokenRefreshView: Recibe 'refresh' -> Retorna un nuevo { access } válido
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# drf_yasg: Herramienta que genera automáticamente documentación interactiva
# de todos los endpoints de nuestra API en formato OpenAPI / Swagger.
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de la vista de documentación Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Sullivan API - Jardín Infantil",
        default_version='v1',
        description=(
            "Documentación interactiva de la API REST del Jardín Sullivan.\n"
            "Permite probar directamente todos los endpoints de usuarios, "
            "estudiantes, cursos, materias, notas y asistencia."
        ),
        contact=openapi.Contact(email="contacto@sullivan.edu.co"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # --------------------------------------------------------------------------
    # 1. AUTENTICACIÓN JWT (JSON Web Tokens)
    # --------------------------------------------------------------------------
    # React usa estos endpoints para obtener y renovar tokens de sesión
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --------------------------------------------------------------------------
    # 2. PANEL DE ADMINISTRACIÓN GRÁFICO DE DJANGO
    # --------------------------------------------------------------------------
    # Interfaz web interna para gestionar datos directamente sin tocar la base de datos
    path('admin/', admin.site.urls),

    # --------------------------------------------------------------------------
    # 3. DOCUMENTACIÓN DE LA API REST
    # --------------------------------------------------------------------------
    # /swagger/ : Interfaz gráfica interactiva para explorar y ejecutar peticiones
    # /redoc/   : Documentación técnica estructurada en formato libro
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # --------------------------------------------------------------------------
    # 4. MÓDULOS DE NEGOCIO (RUTAS MODULARES DE CADA APP)
    # --------------------------------------------------------------------------
    # Cada línea delega el prefijo de la URL al archivo urls.py de su respectiva carpeta.
    path('usuarios/', include('usuarios.urls')),          # Login personalizado, registro y contraseñas
    path('personas/', include('personas.urls')),          # Perfiles de profesores, acudientes y directivos
    path('estudiantes/', include('estudiantes.urls')),    # Ficha de estudiantes y vinculación de acudientes
    path('cursos/', include('cursos.urls')),              # Grados o niveles (Párvulos, etc.)
    path('materias/', include('materias.urls')),          # Asignaturas
    path('asignaciones/', include('asignaciones.urls')),  # Relaciones Profesor <-> Curso <-> Materia
    path('clases/', include('clases.urls')),              # Asistencia diaria por clase
    path('actividades/', include('actividades.urls')),    # Tareas, calificaciones y entregables
    path('eventos/', include('eventos.urls')),            # Eventos del colegio
    path('academico/', include('academico.urls')),        # Períodos y boletines de notas
]

# ------------------------------------------------------------------------------
# 5. SERVIR ARCHIVOS SUBIDOS POR USUARIOS (MEDIA) EN DESARROLLO
# ------------------------------------------------------------------------------
# En producción, un servidor web como Nginx o Cloud Storage entrega los archivos multimedia.
# En modo DEBUG local, Django mismo se encarga de servir las fotos y entregables en /media/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
