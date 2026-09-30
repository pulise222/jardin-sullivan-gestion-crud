from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import CursoProfesorMateria, Persona, PersonaEstudiante
from .serializers import PersonaSerializer, CargaEstudiantesSerializer
from asignaciones.serializers import CursoProfesorMateriaSerializer
from cursos.serializers import CursoSerializer
from cursos.models import Curso
from materias.models import Materia
from usuarios.models import Usuario
from estudiantes.models import Estudiante

from openpyxl import load_workbook
import csv, io


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def persona_me(request):
    """
    GET  -> retorna la Persona del usuario
    PATCH -> actualiza parcialmente la Persona (y Usuario anidado si viene)
    """
    try:
        persona = request.user.persona
    except Persona.DoesNotExist:
        return Response({"detail": "Persona no encontrada para este usuario."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(PersonaSerializer(persona, context={'request': request}).data)

    # PATCH
    serializer = PersonaSerializer(persona, data=request.data, partial=True)
    if serializer.is_valid():
        persona_actualizada = serializer.save()
        return Response(PersonaSerializer(persona_actualizada, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_cursos_profesor(request, persona_id):
    """
    Lista todos los cursos y materias asignadas a un profesor específico.
    GET /personas/{persona_id}/cursos-materias/
    """
    profesor = get_object_or_404(Persona, id=persona_id)
    asignaciones = CursoProfesorMateria.objects.filter(persona=profesor)
    serializer = CursoProfesorMateriaSerializer(asignaciones, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def asignar_curso_materia_profesor(request, persona_id, curso_id, materia_id):
    """
    Asigna curso y materia a un profesor.
    POST /personas/{persona_id}/cursos/{curso_id}/materias/{materia_id}/
    """
    persona = get_object_or_404(Persona, id=persona_id)
    curso = get_object_or_404(Curso, id=curso_id)
    materia = get_object_or_404(Materia, id=materia_id)

    obj, created = CursoProfesorMateria.objects.get_or_create(
        persona=persona,
        curso=curso,
        materia=materia
    )

    serializer = CursoProfesorMateriaSerializer(obj)
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )



@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def eliminar_curso_profesor(request, persona_id, curso_id, materia_id):
    """
    Elimina la asignación curso-materia de un profesor.
    DELETE /personas/{persona_id}/cursos/{curso_id}/materias/{materia_id}/
    """
    asignacion = CursoProfesorMateria.objects.filter(
        persona_id=persona_id,
        curso_id=curso_id,
        materia_id=materia_id
    ).first()

    if asignacion:
        asignacion.delete()
        return Response(
            {"detail": "Asignación eliminada correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )

    return Response(
        {"detail": "Asignación no encontrada."},
        status=status.HTTP_404_NOT_FOUND
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_personas(request):
    """
    GET /personas/buscar?q=texto
    Si q son dígitos -> filtra por numero_documento (icontains)
    Si q tiene texto  -> filtra por nombre/apellido (icontains)
    """
    q = (request.GET.get('q') or '').strip()
    qs = Persona.objects.all()
    if q:
        if q.isdigit():
            qs = qs.filter(numero_documento__icontains=q)
        else:
            qs = qs.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
    qs = qs.order_by('apellido','nombre')[:20]
    return Response(PersonaSerializer(qs, many=True, context={'request': request}).data)




@api_view(['POST','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def persona_avatar(request, persona_id):
    persona = get_object_or_404(Persona, pk=persona_id)

    if request.method in ['POST', 'PATCH']:
        f = request.FILES.get('foto')
        if not f:
            return Response({'detail': "Envíe archivo 'foto'."}, status=400)
        persona.foto = f
        persona.save()
        return Response(PersonaSerializer(persona, context={'request': request}).data)

    # DELETE
    persona.foto.delete(save=True)
    return Response(PersonaSerializer(persona, context={'request': request}).data)