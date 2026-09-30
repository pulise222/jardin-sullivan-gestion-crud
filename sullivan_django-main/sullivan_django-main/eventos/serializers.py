#eventos/serializers.py
from rest_framework import serializers
from .models import Evento

class EventoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = '__all__'  # incluye id_evento, titulo, descripcion, fecha_inicio, imagen
        # DRF agregará imagen e imagen_url (por el SerializerMethodField)

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        try:
            url = obj.imagen.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None