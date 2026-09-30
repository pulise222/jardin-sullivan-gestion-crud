# actividades/serializers.py
from rest_framework import serializers
from .models import Actividad, ActividadEstudiante
from academico.escala import CODIGOS_VALIDOS, codigo_de, etiqueta

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
    # Texto del nivel ("Sobresaliente"…) calculado a partir del código guardado en `calificacion`
    nivel = serializers.SerializerMethodField()

    class Meta:
        model = ActividadEstudiante
        fields = ['id','estudiante','estudiante_nombre','entregado_en','calificacion','nivel','entregable_url']

    def validate_calificacion(self, value):
        # La nota es un NIVEL: 1 Deficiente, 2 Aceptable, 3 Sobresaliente (ver academico/escala.py).
        # Antes el backend aceptaba cualquier número (7, -2, 99.9); ahora solo la escala válida.
        if value is not None and codigo_de(value) not in CODIGOS_VALIDOS:
            raise serializers.ValidationError('La evaluación debe ser 1 (Deficiente), 2 (Aceptable) o 3 (Sobresaliente).')
        if value is not None and value != codigo_de(value):
            raise serializers.ValidationError('La evaluación debe ser un número entero: 1, 2 o 3.')
        return value

    def get_nivel(self, obj):
        return etiqueta(obj.calificacion)

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
    nivel = serializers.SerializerMethodField()

    class Meta:
        model = ActividadEstudiante
        fields = [
            'actividad_estudiante_id', 'actividad_id',
            'titulo', 'descripcion', 'fecha', 'fecha_entrega',
            'entregado_en', 'calificacion', 'nivel', 'entregable_url'
        ]

    def get_nivel(self, obj):
        return etiqueta(obj.calificacion)

    def get_entregable_url(self, obj):
        try:
            return obj.entregable.url if obj.entregable else None
        except Exception:
            return None
