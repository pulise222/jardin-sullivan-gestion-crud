from django.db import models

class Evento(models.Model):
    id_evento = models.AutoField(primary_key=True, db_column='ID_Evento')
    titulo = models.CharField(max_length=255, db_column='Titulo')
    descripcion = models.TextField(null=True, blank=True, db_column='Descripcion')
    fecha_inicio = models.DateTimeField(null=True, blank=True, db_column='Fecha_Inicio')

    # NUEVO: imagen para carrusel
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True, db_column='Imagen')

    # Eliminados: ubicacion, fecha_fin
    # Eliminado: modelo UsuarioEvento (relación por usuario)

    class Meta:
        db_table = 'evento'

    def __str__(self):
        return self.titulo
