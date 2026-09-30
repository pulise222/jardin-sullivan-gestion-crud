"""
================================================================================
PERMISOS BASADOS EN ROLES (RBAC) - PROYECTO SULLIVAN
================================================================================
En Django REST Framework (DRF), las clases de permisos controlan QUIÉN puede
acceder a un endpoint y QUÉ acciones tiene permitido realizar (GET, POST, DELETE...).

¿Cómo funciona la verificación de permisos en DRF?
  1. El cliente envía su token en la cabecera: 'Authorization: Bearer <token>'.
  2. DRF autentica la petición y coloca el objeto usuario en 'request.user'.
  3. Antes de ejecutar la lógica de la vista, DRF llama al método:
       has_permission(self, request, view)
     - Si devuelve True: La petición continúa.
     - Si devuelve False: DRF responde inmediatamente con HTTP 403 Forbidden.
  4. Si la petición opera sobre un registro específico (ej. /estudiantes/5/):
     DRF llama a:
       has_object_permission(self, request, view, obj)
     lo que permite verificar si ese registro pertenece al usuario autenticado.
================================================================================
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdministrador(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol 'Administrador' o superusuarios.
    Se utiliza en endpoints sensibles como importación masiva de alumnos,
    creación/eliminación de cursos, materias y asignación de profesores.
    """
    message = "Acceso denegado: Se requiere rol de Administrador para realizar esta acción."

    def has_permission(self, request, view):
        # 1. Comprobar que el usuario ha iniciado sesión
        if not (request.user and request.user.is_authenticated):
            return False

        # 2. Comprobar que tiene rol Administrador o permisos de staff/superuser en Django
        return bool(
            request.user.rol == 'Administrador' or
            request.user.is_staff or
            request.user.is_superuser
        )


class IsProfesor(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol 'Profesor'.
    Se utiliza en la toma de asistencias, calificación de actividades y
    consulta de cursos asignados al docente.
    """
    message = "Acceso denegado: Se requiere rol de Profesor para realizar esta acción."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.rol == 'Profesor')


class IsAcudiente(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol 'Acudiente'.
    Se utiliza en el portal de padres para consultar notas, eventos y
    asistencia de sus hijos.
    """
    message = "Acceso denegado: Se requiere rol de Acudiente para realizar esta acción."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.rol == 'Acudiente')


class IsAdminOrReadOnly(BasePermission):
    """
    Permiso muy común en APIs REST:
    - Cualquier usuario autenticado puede LEER datos (GET, HEAD, OPTIONS).
    - Solo los usuarios 'Administrador' pueden CREAR, MODIFICAR o BORRAR (POST, PUT, PATCH, DELETE).

    Ejemplo de uso: Catálogos generales de Materias o Cursos (todos necesitan ver la
    lista de materias, pero solo el director puede crear una materia nueva o eliminarla).
    """
    message = "Solo administradores pueden crear, modificar o eliminar este recurso."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # SAFE_METHODS son métodos de solo lectura: ('GET', 'HEAD', 'OPTIONS')
        if request.method in SAFE_METHODS:
            return True

        # Si el método altera datos (POST, PUT, PATCH, DELETE), exige rol Administrador
        return bool(
            request.user.rol == 'Administrador' or
            request.user.is_staff or
            request.user.is_superuser
        )


class IsProfesorOrAdmin(BasePermission):
    """
    Permite el acceso tanto a Profesores como a Administradores.
    Útil para consultar listados de estudiantes por curso o planillas de notas.
    """
    message = "Acceso denegado: Requiere rol de Profesor o Administrador."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(
            request.user.rol in ('Profesor', 'Administrador') or
            request.user.is_staff or
            request.user.is_superuser
        )
