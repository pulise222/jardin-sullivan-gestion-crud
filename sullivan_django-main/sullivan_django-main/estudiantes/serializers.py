from rest_framework import serializers
from .models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    class Meta:
        model = Estudiante
        fields = '__all__'

    def get_foto_url(self, obj):
        if not obj.foto:
            return None
        request = self.context.get('request')
        try:
            url = obj.foto.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None
        
class EstudianteMiniSerializer(serializers.ModelSerializer):
    curso = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()
    class Meta:
        model = Estudiante
        fields = [
            'id','nombre','apellido',
            'tipo_documento','numero_documento',
            'telefono','direccion','correo_electronico',
            'fecha_nacimiento',
            'curso', 'foto_url'
        ]

    def get_curso(self, obj):
        c = getattr(obj, 'curso', None)
        if not c: return None
        return {'id': c.id, 'nombre_curso': getattr(c, 'nombre_curso', str(c))}
    
    def get_foto_url(self, obj):
        if not obj.foto:
            return None
        request = self.context.get('request')
        try:
            url= obj.foto.url if obj.foto else None
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None
