"""
================================================================================
MODELO DE ACTIVIDADES Y ENTREGAS - PROYECTO SULLIVAN
================================================================================
Este archivo modela el sistema evaluativo del colegio:
  1. Actividad: Tarea, taller, proyecto o examen propuesto por un docente.
  2. ActividadEstudiante: La entrega, nota y retroalimentación para cada alumno.
================================================================================
"""

from django.db import models
from estudiantes.models import Estudiante
from personas.models import CursoProfesorMateria
from academico.models import Periodo


class Actividad(models.Model):
    """
    Representa una actividad académica asignada a un curso y materia específicos.
    """
    titulo = models.CharField(
        max_length=100,
        help_text="Título de la tarea o evaluación"
    )
    descripcion = models.TextField(
        help_text="Instrucciones detalladas de la actividad"
    )
    fecha = models.DateField(
        help_text="Fecha en que se asigna la actividad"
    )
    fecha_entrega = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha límite para la entrega de los estudiantes"
    )

    # Período académico (1, 2, 3 o 4) al que pertenece la nota
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Período escolar al que suma esta calificación"
    )

    # Peso porcentual en el cálculo de la nota final (ejemplo: 20% = 20.0)
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Porcentaje o peso ponderado de la actividad en la materia"
    )

    # Relación con la asignación docente (CursoProfesorMateria)
    # Permite saber qué docente, en qué materia y en qué curso se creó la actividad
    asignada_por = models.ForeignKey(
        CursoProfesorMateria,
        on_delete=models.CASCADE,
        related_name='actividades',
        null=True,
        blank=True,
        help_text="Profesor, materia y curso que originan esta actividad"
    )

    class Meta:
        db_table = 'actividad'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.titulo} ({self.asignada_por})"


class ActividadEstudiante(models.Model):
    """
    Representa el estado individual de una actividad para un estudiante concreto.
    Almacena:
      - Si fue entregada o está pendiente
      - El archivo adjunto del alumno (PDF, imagen, etc.)
      - La calificación asignada por el profesor (ej. 4.5 sobre 5.0)
    """
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='actividades_asignadas',
        help_text="Estudiante evaluado"
    )
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='entregas',
        help_text="Actividad evaluada"
    )
    entregado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Marca temporal de cuándo se realizó la entrega"
    )
    entregable = models.FileField(
        upload_to='entregables/',
        null=True,
        blank=True,
        help_text="Archivo de la tarea subido por el alumno o acudiente"
    )
    # Calificación con 1 decimal (ejemplo: 3.5, 4.0, 5.0)
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Nota cuantitativa de 0.0 a 5.0"
    )

    class Meta:
        # unique_together garantiza que un estudiante no tenga dos notas para la misma actividad
        unique_together = ('estudiante', 'actividad')
        db_table = 'actividad_estudiante'

    def __str__(self):
        return f"{self.estudiante} - {self.actividad.titulo}: {self.calificacion or 'Sin calificar'}"
