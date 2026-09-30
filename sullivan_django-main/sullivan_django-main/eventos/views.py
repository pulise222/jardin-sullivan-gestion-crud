from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Evento
from .serializers import EventoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all().order_by('-fecha_inicio', '-id_evento')
    serializer_class = EventoSerializer

    @action(detail=False, methods=['get'], url_path='proximos')
    def proximos(self, request):
        """
        Lista eventos cuya fecha_inicio es >= ahora, orden ascendente.
        ?limit=10 para limitar cantidad (opcional)
        """
        now = timezone.now()
        qs = Evento.objects.filter(fecha_inicio__gte=now).order_by('fecha_inicio', 'id_evento')
        try:
            limit = int(request.query_params.get('limit', '10'))
        except ValueError:
            limit = 10
        qs = qs[:max(1, min(limit, 50))]
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)
