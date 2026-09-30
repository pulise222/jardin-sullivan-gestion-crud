"""
================================================================================
CONFIGURACIÓN PRINCIPAL DE DJANGO - PROYECTO SULLIVAN
================================================================================
Este archivo contiene todos los ajustes y parámetros de configuración del Backend.
Django lee este archivo al iniciar el servidor para saber:
  1. Dónde están ubicados los archivos del proyecto (BASE_DIR).
  2. Qué aplicaciones y módulos están habilitados (INSTALLED_APPS).
  3. Cómo procesar las peticiones HTTP que llegan de React (MIDDLEWARE).
  4. A qué base de datos conectarse (DATABASES: SQLite / MySQL).
  5. Cómo autenticar a los usuarios mediante JWT (REST_FRAMEWORK & SIMPLE_JWT).
  6. Cómo permitir que el Frontend en React se comunique sin bloqueos (CORS).
================================================================================
"""

import os
from pathlib import Path
from datetime import timedelta

# ==============================================================================
# 1. RUTAS BASE DEL PROYECTO
# ==============================================================================
# BASE_DIR apunta a la carpeta raíz del proyecto backend (donde está manage.py).
# Path(__file__).resolve().parent.parent sube dos niveles desde este archivo.
# Nos permite referenciar archivos con rutas relativas seguras: BASE_DIR / 'media'
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# 2. SEGURIDAD BÁSICA (DESARROLLO VS PRODUCCIÓN)
# ==============================================================================
# SECRET_KEY: Clave criptográfica única usada por Django para firmar cookies,
# sesiones y tokens de restablecimiento de contraseña. En producción debe leerse
# desde una variable de entorno para no exponerla en el repositorio.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-3rtuj%swwk)d9!&vt^w=3)0fqe$cw-q2ft3v^&$kds4gssjt5)'
)

# DEBUG: Cuando es True, Django muestra páginas de error detalladas con traceback
# útil para desarrolladores. En producción DEBE ser False para no revelar código.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1')

# Freno de seguridad: si alguien publica el proyecto con DEBUG apagado (producción) pero olvida
# definir su propia clave secreta, Django se niega a arrancar en lugar de usar la del repositorio.
if not DEBUG and SECRET_KEY.startswith('django-insecure'):
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Define DJANGO_SECRET_KEY antes de ejecutar con DJANGO_DEBUG=False (ver .env.example).')

# ALLOWED_HOSTS: Lista de dominios o IPs desde los cuales se puede acceder al backend.
# Por defecto solo la máquina local (antes era '*', que acepta cualquier dominio).
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Ruta opcional de wkhtmltopdf (para exportar reportes HTML a PDF)
WKHTMLTOPDF_CMD = os.environ.get('WKHTMLTOPDF_CMD', r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")


# ==============================================================================
# 3. APLICACIONES INSTALADAS (INSTALLED_APPS)
# ==============================================================================
# Django divide la funcionalidad en "apps" (módulos).
# Cada app tiene sus propios modelos (tablas), vistas (lógica) y rutas (urls).
INSTALLED_APPS = [
    # --- Apps estándar que provee Django por defecto ---
    'django.contrib.admin',          # Panel administrativo gráfico (/admin/)
    'django.contrib.auth',           # Sistema de autenticación de usuarios y permisos
    'django.contrib.contenttypes',   # Sistema de tipos de contenido para relaciones genéricas
    'django.contrib.sessions',       # Manejo de sesiones de usuario en el servidor
    'django.contrib.messages',       # Sistema de mensajes flash (alertas temporales)
    'django.contrib.staticfiles',    # Manejo de archivos CSS, JS e imágenes del admin

    # --- Librerías externas de terceros ---
    'corsheaders',                   # Permite peticiones desde orígenes externos (Cross-Origin)
    'rest_framework',                # Django REST Framework: convierte Django en una API REST
    'rest_framework.authtoken',      # Autenticación basada en tokens estándar de DRF
    'rest_framework_simplejwt',      # Autenticación basada en JSON Web Tokens (JWT)
    'drf_yasg',                      # Generador automático de documentación Swagger / OpenAPI

    # --- Módulos propios del Jardín Sullivan ---
    'usuarios',                      # Modelo personalizado de Usuario con roles (Admin, Profe, Acudiente)
    'personas',                      # Datos de contacto y perfil vinculados a cada Usuario
    'estudiantes',                   # Registro de alumnos, documentos de identidad y cursos
    'cursos',                        # Grados o niveles académicos (Párvulos, etc.)
    'materias',                      # Asignaturas impartidas (Arte, etc.)
    'clases',                        # Sesiones de clase y registro de asistencia diaria
    'actividades',                   # Tareas, talleres, entregables y matriz de notas
    'asignaciones',                  # Mapeo de relación Profesor <-> Curso <-> Materia
    'eventos',                       # Actividades extracurriculares y calendario escolar
    'academico',                     # Períodos y boletines académicos
]


# ==============================================================================
# 4. MIDDLEWARES (TUBERÍA DE PROCESAMIENTO DE PETICIONES)
# ==============================================================================
# Los middlewares son capas intermedias que interceptan CADA petición que llega
# antes de llegar a la vista, y CADA respuesta antes de volver al cliente (React).
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # IMPORTANTE: CorsMiddleware debe ir antes de CommonMiddleware para que
    # las respuestas a solicitudes OPTIONS (pre-flight de los navegadores)
    # incluyan las cabeceras CORS necesarias.
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Archivo de entrada donde están mapeadas las rutas URLs principales del servidor
ROOT_URLCONF = 'sullivan_django.urls'

# Configuración del motor de plantillas HTML (usado principalmente por el panel /admin)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicación WSGI (Web Server Gateway Interface) para servidores en producción
WSGI_APPLICATION = 'sullivan_django.wsgi.application'


# ==============================================================================
# 5. BASE DE DATOS (DATABASES)
# ==============================================================================
# Por defecto usamos SQLite (db.sqlite3) porque está embebido en Python y no
# requiere servicios de fondo. Si defines la variable de entorno USE_MYSQL=1,
# se conectará a MySQL en el puerto 3306 (por ejemplo mediante XAMPP).
USE_MYSQL = os.environ.get('USE_MYSQL', 'False').lower() in ('true', '1')

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'sullivan'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==============================================================================
# 6. MODELO DE USUARIO PERSONALIZADO (AUTH_USER_MODEL)
# ==============================================================================
# Por defecto Django incluye un modelo User genérico. Aquí le decimos que use
# nuestro propio modelo 'usuarios.Usuario', el cual extiende de AbstractUser
# y agrega el campo de selección de 'rol' ('Administrador', 'Profesor', 'Acudiente').
AUTH_USER_MODEL = 'usuarios.Usuario'

# Validadores para exigir contraseñas robustas al registrar o cambiar claves
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================================
# 7. DJANGO REST FRAMEWORK & SIMPLE JWT
# ==============================================================================
# DRF convierte las respuestas de Django a formato JSON para que React las consuma.
REST_FRAMEWORK = {
    # Clases de autenticación: verifica quién es el usuario en cada petición.
    # Prioridad: JWT (Bearer <token>).
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    # Permiso por defecto: Exigir que el usuario esté autenticado para cualquier endpoint
    # a menos que la vista declare explícitamente permission_classes = [AllowAny].
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Parsers: Permite recibir peticiones en JSON puro o con archivos adjuntos (multipart)
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
}

# Configuración de tiempos de vida para los tokens JWT
SIMPLE_JWT = {
    # Access Token: se envía en la cabecera 'Authorization: Bearer <token>' en cada petición.
    # En desarrollo le damos 1 día para no tener que iniciar sesión a cada momento al probar.
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # Refresh Token: token de larga duración usado por React para pedir un nuevo Access Token.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ==============================================================================
# 8. CORS (CROSS-ORIGIN RESOURCE SHARING)
# ==============================================================================
# Por seguridad, los navegadores web bloquean peticiones JavaScript desde un dominio/puerto
# (ej. http://localhost:5173 de React) hacia otro (ej. http://127.0.0.1:8000 de Django).
# Antes se permitía CUALQUIER origen (CORS_ALLOW_ALL_ORIGINS = True), lo que deja que cualquier
# página web haga peticiones a la API. Ahora solo se aceptan los orígenes de la lista; por defecto
# el servidor de desarrollo de React. Para publicar, define DJANGO_CORS_ORIGINS con la URL del front.
CORS_ALLOWED_ORIGINS = os.environ.get(
    'DJANGO_CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True


# ==============================================================================
# 9. INTERNACIONALIZACIÓN Y ZONA HORARIA
# ==============================================================================
LANGUAGE_CODE = 'es-co'   # Español (Colombia)
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# 10. ARCHIVOS ESTÁTICOS Y MULTIMEDIA (MEDIA & STATIC)
# ==============================================================================
# STATIC: Archivos del sistema (CSS/JS del panel administrativo de Django)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA: Archivos que los usuarios suben dinámicamente (fotos de perfil, fotos de
# estudiantes, archivos de entregables o tareas subidos por alumnos o profesores).
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tipo por defecto de clave primaria autoincremental
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# 11. CORREO ELECTRÓNICO (RESTABLECIMIENTO DE CONTRASEÑA)
# ==============================================================================
# En desarrollo usamos el backend de consola: cuando un usuario pide restablecer
# su contraseña, Django imprime el correo con el enlace en la terminal en vez de
# intentar enviar un correo real por SMTP.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@sullivan.edu.co'
FRONTEND_RESET_URL = os.environ.get('FRONTEND_RESET_URL', 'http://localhost:5173/reset-password')
