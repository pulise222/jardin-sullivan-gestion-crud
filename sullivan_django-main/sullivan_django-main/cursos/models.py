"""
================================================================================
MODELO DE CURSOS - PROYECTO SULLIVAN
================================================================================
Representa un grupo, nivel o grado escolar del jardín de infantes
(ejemplos: Párvulos A, Párvulos B, Jardín 1, Pre-jardín, etc.).
================================================================================
"""

from django.db import models


class Curso(models.Model):
    """
    Un curso agrupa a un conjunto de estudiantes de edades similares
    y cuenta con materias y profesores asignados.
    """
    nombre_curso = models.CharField(
        max_length=100,
        help_text="Nombre del grado o curso (ej. Párvulos A)"
    )
    descripcion = models.TextField(
        help_text="Descripción pedagógica, objetivos o rango de edad del curso"
    )

    class Meta:
        db_table = 'curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nombre_curso
