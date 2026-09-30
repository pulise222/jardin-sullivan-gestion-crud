"""
================================================================================
MODELO DE ESTUDIANTES - PROYECTO SULLIVAN
================================================================================
¿Qué es un Modelo en Django?
Un modelo es una clase de Python que define la estructura de una tabla en la
base de datos (columnas, tipos de datos, restricciones y relaciones).
El ORM (Object-Relational Mapping) de Django traduce automáticamente los métodos
de Python a consultas SQL (SELECT, INSERT, UPDATE, DELETE).
================================================================================
"""

from django.db import models
from cursos.models import Curso


class Estudiante(models.Model):
    """
    Representa a un alumno matriculado en el Jardín Sullivan.
    Cada estudiante está asignado obligatoriamente a un curso (grado académico).
    """

    # Opciones predefinidas para el tipo de documento.
    # En la base de datos se guarda la clave ('RC', 'TI') y en los formularios
    # se muestra la etiqueta amigable ('Registro Civil', 'Tarjeta de Identidad').
    TIPO_DOC_CHOICES = (
        ('RC', 'Registro Civil'),
        ('TI', 'Tarjeta de Identidad'),
    )

    # Campos de texto y contacto
    nombre = models.CharField(
        max_length=100,
        help_text="Nombres del estudiante"
    )
    apellido = models.CharField(
        max_length=100,
        help_text="Apellidos del estudiante"
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento para cálculo de edad escolar"
    )
    direccion = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Lugar de residencia familiar"
    )
    telefono = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Teléfono de contacto de emergencia"
    )
    correo_electronico = models.EmailField(
        null=True,
        blank=True,
        help_text="Correo institucional o de contacto del alumno"
    )
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOC_CHOICES,
        null=True,
        blank=True
    )
    numero_documento = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Número de documento de identidad oficial"
    )

    # ImageField: Gestiona la subida de fotos.
    # 'upload_to' define la subcarpeta dentro de MEDIA_ROOT donde se guardará el archivo físico.
    foto = models.ImageField(
        upload_to='avatars/estudiantes/',
        null=True,
        blank=True,
        help_text="Foto de perfil del estudiante"
    )

    # --------------------------------------------------------------------------
    # RELACIÓN CON EL CURSO (CLAVE FORÁNEA / FOREIGN KEY)
    # --------------------------------------------------------------------------
    # ForeignKey representa una relación de Muchos a Uno (Muchos estudiantes pertenecen a Un curso).
    #
    # ¿Por qué usar on_delete=models.PROTECT en vez de models.CASCADE?
    #   - Con CASCADE: Si un administrador elimina un curso, la base de datos
    #     borraría automáticamente a TODOS los niños matriculados en él.
    #   - Con PROTECT: Django impide eliminar el curso si todavía tiene estudiantes,
    #     lanzando un error protector y evitando la pérdida irreversible de datos.
    #
    # related_name='estudiantes' permite consultar desde un curso todos sus alumnos:
    #   ejemplo: mi_curso.estudiantes.all()
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name='estudiantes',
        help_text="Curso o grado al que pertenece el estudiante"
    )

    class Meta:
        # Nombre exacto que tendrá la tabla física en la base de datos (SQLite / MySQL)
        db_table = 'estudiante'

        # Índices de base de datos: Aceleran drásticamente las búsquedas frecuentes.
        # Al indexar tipo_documento + numero_documento, buscar a un alumno por documento
        # es casi instantáneo incluso con miles de registros.
        indexes = [
            models.Index(fields=['tipo_documento', 'numero_documento']),
        ]

    def __str__(self):
        """
        Representación legible en texto del objeto (usada en el panel Admin de Django).
        """
        return f"{self.nombre} {self.apellido}"
