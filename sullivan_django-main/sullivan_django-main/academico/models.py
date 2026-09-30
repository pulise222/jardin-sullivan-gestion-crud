# academico/models.py
from django.db import models
from personas.models import CursoProfesorMateria

        
class Periodo(models.Model):
    anio = models.PositiveSmallIntegerField()
    numero = models.PositiveSmallIntegerField()  # 1,2,3,4...
    nombre = models.CharField(max_length=50, blank=True)  # "II Periodo", etc.
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'periodo'
        unique_together = ('anio', 'numero')
        ordering = ['anio', 'numero']

    def __str__(self): return f'{self.anio} - P{self.numero}'


class Logro(models.Model):
    cpm = models.ForeignKey(CursoProfesorMateria, on_delete=models.CASCADE, related_name='logros')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    descripcion = models.TextField()
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = 'logro'
        unique_together = ('cpm', 'periodo', 'orden')
        ordering = ['cpm_id', 'periodo_id', 'orden']


class NotaMateriaPeriodo(models.Model):
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)
    cpm = models.ForeignKey(CursoProfesorMateria, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    promedio = models.DecimalField(max_digits=3, decimal_places=1)  # 0.0 – 5.0
    desempeño = models.CharField(max_length=20, blank=True)         # BAJO/BÁSICO/ALTO/SUPERIOR
    inasistencias = models.PositiveSmallIntegerField(default=0)
    observacion_docente = models.TextField(blank=True)
    calculada = models.BooleanField(default=True)  # viene de cálculo (no manual)

    class Meta:
        db_table = 'nota_materia_periodo'
        unique_together = ('estudiante', 'cpm', 'periodo')