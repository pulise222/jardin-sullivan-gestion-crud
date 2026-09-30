# actividades/serializers.py
from rest_framework import serializers
from .models import Actividad, ActividadEstudiante

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ['id','titulo','descripcion','fecha','fecha_entrega','asignada_por']

class ActividadCreateSerializer(serializers.ModelSerializer):
    cpm_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Actividad
        fields = ['id','titulo','descripcion','fecha','fecha_entrega','cpm_id']

    def create(self, validated_data):
        cpm_id = validated_data.pop('cpm_id')
        from personas.models import CursoProfesorMateria
        cpm = CursoProfesorMateria.objects.get(id=cpm_id)
        return Actividad.objects.create(asignada_por=cpm, **validated_data)

class ActividadEntregaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    entregable_url = serializers.SerializerMethodField()

    class Meta:
        model = ActividadEstudiante
        fields = ['id','estudiante','estudiante_nombre','entregado_en','calificacion','entregable_url']

    def get_estudiante_nombre(self, obj):
        return f"{obj.estudiante.nombre} {obj.estudiante.apellido}"

    def get_entregable_url(self, obj):
        try:
            return obj.entregable.url if obj.entregable else None
        except Exception:
            return None


class ActividadDetalleSerializer(serializers.ModelSerializer):
    entregas = ActividadEntregaSerializer(many=True, read_only=True)
    class Meta:
        model = Actividad
        fields = ['id','titulo','descripcion','fecha','fecha_entrega','asignada_por','entregas']


class ActividadEntregaFullSerializer(serializers.ModelSerializer):
    actividad_estudiante_id = serializers.IntegerField(source='id', read_only=True)
    actividad_id = serializers.IntegerField(source='actividad.id', read_only=True)
    titulo = serializers.CharField(source='actividad.titulo', read_only=True)
    descripcion = serializers.CharField(source='actividad.descripcion', read_only=True)
    fecha = serializers.DateField(source='actividad.fecha', read_only=True)
    fecha_entrega = serializers.DateField(source='actividad.fecha_entrega', read_only=True)
    entregable_url = serializers.SerializerMethodField()

    class Meta:
        model = ActividadEstudiante
        fields = [
            'actividad_estudiante_id', 'actividad_id',
            'titulo', 'descripcion', 'fecha', 'fecha_entrega',
            'entregado_en', 'calificacion', 'entregable_url'
        ]

    def get_entregable_url(self, obj):
        try:
            return obj.entregable.url if obj.entregable else None
        except Exception:
            return None
