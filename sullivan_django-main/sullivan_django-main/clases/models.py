# clases/models.py
from django.db import models
from estudiantes.models import Estudiante
from personas.models import CursoProfesorMateria

class Asistencia(models.Model):
    ESTADOS = (('Presente', 'Presente'), ('Tarde', 'Tarde'), ('Ausente', 'Ausente') )

    # NUEVO: relación directa
    cpm       = models.ForeignKey(
        CursoProfesorMateria,
        on_delete=models.CASCADE,
        related_name='asistencias',
        null=True, blank=True
    )
    fecha     = models.DateField(null=True, blank= True)
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='asistencias', 
        null=True, blank=True
    )
    estado    = models.CharField(max_length=8, choices=ESTADOS)

    class Meta:
        db_table = 'asistencia'
        unique_together = (('cpm', 'fecha', 'estudiante'),)  # evita doble asistencia
        indexes = [models.Index(fields=['cpm', 'fecha'])]
