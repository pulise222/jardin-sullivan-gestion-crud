"""
================================================================================
MODELO DE MATERIAS - PROYECTO SULLIVAN
================================================================================
Representa las áreas del conocimiento o asignaturas impartidas en el jardín
(ejemplos: Arte y Creatividad, Música, Psicomotricidad, Inglés, etc.).
================================================================================
"""

from django.db import models


class Materia(models.Model):
    """
    Catálogo de materias disponibles en el currículo del jardín infantil.
    """
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre de la asignatura o área de aprendizaje"
    )

    class Meta:
        db_table = 'materia'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return self.nombre
