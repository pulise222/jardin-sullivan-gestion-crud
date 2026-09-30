# asignaciones/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from personas.models import CursoProfesorMateria
from .serializers import CursoProfesorMateriaSerializer

class CursoProfesorMateriaViewSet(viewsets.ModelViewSet):
    """
    Endpoints REST:
    GET    /asignaciones/              -> listar (con filtros)
    POST   /asignaciones/              -> crear  {curso_id, persona_id, materia_id}
    GET    /asignaciones/{id}/         -> detalle
    PATCH  /asignaciones/{id}/         -> actualizar
    DELETE /asignaciones/{id}/         -> eliminar
    """
    queryset = (CursoProfesorMateria.objects
                .select_related('curso', 'materia', 'persona'))
    serializer_class = CursoProfesorMateriaSerializer
    permission_classes = [IsAuthenticated]

    # Filtros útiles en tabla (opcional)
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['curso', 'materia', 'persona']  # ?curso=1&persona=5
    search_fields = [
        'curso__nombre_curso',
        'materia__nombre',
        'persona__nombre',
        'persona__apellido',
    ]
    ordering_fields = ['id', 'curso__nombre_curso', 'materia__nombre']
    ordering = ['id']

    def create(self, request, *args, **kwargs):
        """
        Respetará unique_together (persona, curso, materia).
        Si el registro ya existe, puedes devolver 200 en lugar de 400
        (descomenta el get_or_create si prefieres ese comportamiento).
        """
        # # Ejemplo de get_or_create si lo quieres idempotente:
        # data = request.data
        # obj, created = CursoProfesorMateria.objects.get_or_create(
        #     persona_id=data.get('persona_id'),
        #     curso_id=data.get('curso_id'),
        #     materia_id=data.get('materia_id'),
        # )
        # ser = self.get_serializer(obj)
        # return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='upsert', permission_classes=[IsAuthenticated])
    def upsert(self, request):
        """
        POST /asignaciones/upsert/
        Body: {persona_id, curso_id, materia_id}
        Crea si no existe, devuelve el existente si ya estaba.
        """
        data = request.data
        obj, created = CursoProfesorMateria.objects.get_or_create(
            persona_id=data.get('persona_id'),
            curso_id=data.get('curso_id'),
            materia_id=data.get('materia_id'),
        )
        ser = self.get_serializer(obj)
        return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
