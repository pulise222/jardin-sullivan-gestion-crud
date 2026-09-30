# clases/serializers.py
from rest_framework import serializers
from .models import Asistencia

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ['id', 'cpm', 'fecha', 'estudiante', 'estado']
