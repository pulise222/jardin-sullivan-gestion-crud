from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Profesor', 'Profesor'),
        ('Acudiente', 'Acudiente'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)


    class Meta:
        db_table = 'usuario'


    def __str__(self):
        return f"{self.username} ({self.rol})"
