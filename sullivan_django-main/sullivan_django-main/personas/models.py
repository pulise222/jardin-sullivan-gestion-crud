"""
================================================================================
MODELO DE PERSONAS Y RELACIONES - PROYECTO SULLIVAN
================================================================================
En este archivo se modelan los datos de filiación humana y las relaciones:
  1. Persona: Perfil con datos personales (nombre, teléfono, documento, etc.)
  2. PersonaEstudiante: Tabla intermedia que vincula a un Acudiente con su Estudiante
  3. CursoProfesorMateria: Tabla intermedia que vincula un Profesor con su Curso y Materia
================================================================================
"""

from django.db import models
from cursos.models import Curso
from usuarios.models import Usuario
from materias.models import Materia


class Persona(models.Model):
    """
    Datos biográficos y de contacto de cualquier persona vinculada al jardín
    (profesores, acudientes, directivos, coordinadores).

    ¿Por qué separar Usuario de Persona?
    - 'Usuario' maneja exclusivamente la seguridad (credenciales, contraseña, rol, login).
    - 'Persona' maneja la información del mundo real (documento, teléfono, dirección, foto).
    Esta separación sigue el principio de responsabilidad única en arquitectura de software.
    """

    # OneToOneField: Relación 1 a 1 exacta.
    # Un Usuario tiene exactamente Una Persona, y una Persona pertenece a Un único Usuario.
    # on_delete=models.CASCADE: Si la cuenta de usuario se elimina, su ficha de persona se elimina.
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='persona',
        help_text="Cuenta de usuario de acceso al sistema"
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    tipo_documento = models.CharField(max_length=20)
    numero_documento = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    foto = models.ImageField(upload_to='avatars/personas/', null=True, blank=True)

    class Meta:
        db_table = 'persona'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class PersonaEstudiante(models.Model):
    """
    Tabla intermedia para la relación de Muchos a Muchos entre Acudientes y Estudiantes.
    - Un acudiente puede tener a cargo a varios estudiantes (hermanitos en el jardín).
    - Un estudiante puede tener más de un acudiente (mamá, papá, abuela).

    El campo 'parentesco' describe el vínculo (ej. 'Madre', 'Padre', 'Tutor').
    """
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='estudiantes_a_cargo',
        help_text="Acudiente responsable"
    )
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.CASCADE,
        related_name='acudientes_vinculados',
        help_text="Estudiante a cargo"
    )
    parentesco = models.CharField(
        max_length=30,
        default='Acudiente',
        help_text="Vínculo familiar (Madre, Padre, etc.)"
    )

    class Meta:
        db_table = 'persona_estudiante'

    def __str__(self):
        return f"{self.persona} -> {self.estudiante} ({self.parentesco})"


class CursoProfesorMateria(models.Model):
    """
    Tabla de asignación académica (CPM).
    Define la asignación docente:
      "El profesor X dicta la materia Y en el curso Z".

    Por ejemplo:
      - Profesor: Carlos Pérez
      - Curso: Párvulos A
      - Materia: Arte y Creatividad

    Esta asignación es clave porque todas las actividades, notas y asistencias
    se derivan de esta relación.
    """
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='cursos_profesor',
        help_text="Docente asignado"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='profesores_materia',
        help_text="Curso en el que se dicta la clase"
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='cursos_profesor',
        help_text="Materia asignada"
    )

    class Meta:
        db_table = 'curso_profesor_materia'
        # unique_together: Evita que se asigne dos veces el mismo profesor a la misma materia en el mismo curso
        unique_together = (('persona', 'curso', 'materia'),)

    def __str__(self):
        return f"{self.persona} | {self.materia} | {self.curso}"