"""
================================================================================
VISTAS DE ESTUDIANTES (API REST) - PROYECTO SULLIVAN
================================================================================
En Django REST Framework, las "vistas" son las encargadas de procesar las
peticiones HTTP que llegan desde el Frontend (React).

Existen dos formas principales de crear vistas en DRF:
  1. ViewSets (conjuntos de vistas):
     Clases que agrupan automáticamente todas las operaciones CRUD (Crear, Leer,
     Actualizar, Borrar) en un solo lugar sin tener que escribir código repetitivo.
  2. Vistas basadas en funciones (@api_view):
     Funciones individuales para endpoints con lógica personalizada que no encajan
     en un CRUD estándar (por ejemplo: 'mis_estudiantes' para acudientes).
================================================================================
"""

from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Estudiante
from .serializers import EstudianteSerializer, EstudianteMiniSerializer
from personas.models import Persona, PersonaEstudiante
from personas.serializers import PersonaSerializer
from usuarios.permissions import IsAdminOrReadOnly, IsAdministrador


class EstudianteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de Estudiantes.

    ¿Qué hace ModelViewSet por nosotros?
    Provee automáticamente las 6 acciones estándar de una API REST:
      - GET    /estudiantes/      -> list()            (listar todos los estudiantes)
      - POST   /estudiantes/      -> create()          (crear un nuevo estudiante)
      - GET    /estudiantes/{id}/ -> retrieve()        (ver detalle de un estudiante)
      - PUT    /estudiantes/{id}/ -> update()          (reemplazar datos completos)
      - PATCH  /estudiantes/{id}/ -> partial_update()  (modificar algunos campos)
      - DELETE /estudiantes/{id}/ -> destroy()         (eliminar estudiante)

    Permisos:
      Usamos 'IsAdminOrReadOnly':
      - Lectura (GET): Permitida a cualquier usuario autenticado (Profesores, Acudientes).
      - Escritura (POST, PUT, DELETE): Exclusiva de usuarios con rol 'Administrador'.
    """
    queryset = Estudiante.objects.all().select_related('curso')
    serializer_class = EstudianteSerializer
    permission_classes = [IsAdminOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_estudiantes(request):
    """
    Devuelve los estudiantes vinculados al acudiente que ha iniciado sesión.
    Endpoint: GET /estudiantes/mis_estudiantes/

    Flujo de la función:
      1. Extrae el usuario autenticado desde 'request.user'.
      2. Busca la 'Persona' asociada a ese usuario.
      3. Consulta la tabla 'PersonaEstudiante' para saber qué alumnos tiene a su cargo.
      4. select_related('curso') hace un SQL JOIN para traer el curso del alumno en
         una sola consulta rápida (evita el problema de rendimiento N+1).
      5. Serializa los datos con 'EstudianteMiniSerializer' y los retorna como JSON.
    """
    persona = getattr(request.user, 'persona', None)
    if persona is None:
        return Response({'detail': 'El usuario actual no tiene un perfil de Persona asociado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Buscar los IDs de los estudiantes que tienen a esta persona como acudiente
    est_ids = PersonaEstudiante.objects.filter(persona=persona).values_list('estudiante_id', flat=True)
    qs = Estudiante.objects.select_related('curso').filter(id__in=est_ids)

    data = EstudianteMiniSerializer(qs, many=True, context={'request': request}).data
    return Response(data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def acudientes_de_estudiante(request, estudiante_id):
    """
    Consulta o vincula acudientes a un estudiante específico.
    GET  /estudiantes/{id}/acudientes/  -> Lista las personas acudientes del estudiante.
    POST /estudiantes/{id}/acudientes/  -> Asigna un nuevo acudiente (solo Admin).
         Body: { "persona_id": 5, "parentesco": "Madre" }
    """
    est = get_object_or_404(Estudiante, pk=estudiante_id)

    if request.method == 'GET':
        persona_ids = PersonaEstudiante.objects.filter(estudiante=est).values_list('persona_id', flat=True)
        acudientes = Persona.objects.filter(id__in=persona_ids).order_by('apellido', 'nombre')
        return Response(PersonaSerializer(acudientes, many=True).data)

    # POST: Vincular un acudiente (requiere que el usuario sea Administrador)
    if not (request.user.rol == 'Administrador' or request.user.is_staff or request.user.is_superuser):
        return Response({'detail': 'Solo administradores pueden vincular acudientes.'}, status=status.HTTP_403_FORBIDDEN)

    persona_id = request.data.get('persona_id')
    parentesco = request.data.get('parentesco', 'Acudiente')
    if not persona_id:
        return Response({'detail': 'El campo persona_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

    persona = get_object_or_404(Persona, pk=persona_id)
    PersonaEstudiante.objects.get_or_create(
        persona=persona,
        estudiante=est,
        defaults={'parentesco': parentesco}
    )

    # Devolver la lista actualizada de acudientes
    persona_ids = PersonaEstudiante.objects.filter(estudiante=est).values_list('persona_id', flat=True)
    acudientes = Persona.objects.filter(id__in=persona_ids).order_by('apellido', 'nombre')
    return Response(PersonaSerializer(acudientes, many=True).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAdministrador])
def remover_acudiente_de_estudiante(request, estudiante_id, persona_id):
    """
    Elimina la relación entre un estudiante y un acudiente.
    Endpoint: DELETE /estudiantes/{estudiante_id}/acudientes/{persona_id}/
    Protegido con [IsAdministrador] para evitar que cualquiera desvincule acudientes.
    """
    est = get_object_or_404(Estudiante, pk=estudiante_id)
    PersonaEstudiante.objects.filter(estudiante=est, persona_id=persona_id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def estudiante_avatar(request, estudiante_id):
    """
    Sube, actualiza o elimina la fotografía de un estudiante.
    MultiPartParser permite a Django decodificar archivos binarios (imágenes) enviados en formularios.
    """
    est = get_object_or_404(Estudiante, pk=estudiante_id)

    if request.method in ['POST', 'PATCH']:
        f = request.FILES.get('foto')
        if not f:
            return Response({'detail': "Debe enviar un archivo en el campo 'foto'."}, status=status.HTTP_400_BAD_REQUEST)
        est.foto = f
        est.save()
        return Response(EstudianteSerializer(est, context={'request': request}).data)

    # DELETE: Elimina el archivo físico del disco y limpia el campo
    if est.foto:
        est.foto.delete(save=True)
    return Response(EstudianteSerializer(est, context={'request': request}).data)
