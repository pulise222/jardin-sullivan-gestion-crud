# clases/views.py
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from personas.models import CursoProfesorMateria
from estudiantes.models import Estudiante
from .models import Asistencia
from .serializers import AsistenciaSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asistencia_por_cpm_y_fecha(request, cpm_id):
    """Devuelve estudiantes del curso y su asistencia para la fecha dada."""
    cpm = get_object_or_404(CursoProfesorMateria, id=cpm_id)
    fecha = request.GET.get('fecha') or date.today().isoformat()

    ests = Estudiante.objects.filter(curso_id=cpm.curso_id).values('id', 'nombre', 'apellido')

    asist = {
        (a.estudiante_id): a.estado
        for a in Asistencia.objects.filter(cpm=cpm, fecha=fecha)
    }

    return Response({
        'cpm_id': cpm.id,
        'curso_id': cpm.curso_id,
        'materia_id': cpm.materia_id,
        'fecha': fecha,
        'estudiantes': [
            {
                'estudiante_id': e['id'],
                'nombre': e['nombre'],
                'apellido': e['apellido'],
                'estado': asist.get(e['id'])
            }
            for e in ests
        ]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upsert_asistencia(request, cpm_id):
    """
    Crea/actualiza la asistencia de UN estudiante.
    body: { "fecha":"YYYY-MM-DD", "estudiante_id": 12, "estado": "Presente|Tarde|Ausente" }
    """
    cpm = get_object_or_404(CursoProfesorMateria, id=cpm_id)
    fecha = request.data.get('fecha')
    estudiante_id = request.data.get('estudiante_id')
    estado = request.data.get('estado')

    if estado not in ('Presente', 'Tarde', 'Ausente'):
        return Response({'detail': 'Estado inválido'}, status=400)
    if not (fecha and estudiante_id):
        return Response({'detail': 'fecha y estudiante_id son requeridos'}, status=400)

    obj, _created = Asistencia.objects.update_or_create(
        cpm=cpm, fecha=fecha, estudiante_id=estudiante_id,
        defaults={'estado': estado}
    )
    return Response(AsistenciaSerializer(obj).data, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fechas_con_asistencia(request, cpm_id):
    """Lista de fechas en las que hay asistencia para ese CPM."""
    fechas = (Asistencia.objects
              .filter(cpm_id=cpm_id)
              .order_by('fecha')
              .values_list('fecha', flat=True)
              .distinct())
    return Response({'cpm_id': cpm_id, 'fechas': list(fechas)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen_asistencia_cpm(request, cpm_id: int):
    cpm = get_object_or_404(CursoProfesorMateria.objects.select_related('curso', 'materia'), id=cpm_id)

    fechas_qs = (Asistencia.objects
                 .filter(cpm=cpm)
                 .order_by('fecha')
                 .values_list('fecha', flat=True)
                 .distinct())
    fechas = [f.isoformat() for f in fechas_qs]

    estudiantes_qs = Estudiante.objects.filter(curso_id=cpm.curso_id).values('id', 'nombre', 'apellido')

    asistencias = {}
    for a in Asistencia.objects.filter(cpm=cpm).only('estudiante_id', 'fecha', 'estado'):
        asistencias.setdefault(a.estudiante_id, {})[a.fecha.isoformat()] = a.estado

    estudiantes_payload = []
    for e in estudiantes_qs:
        estudiantes_payload.append({
            'id': e['id'],
            'nombre': e['nombre'],
            'apellido': e['apellido'],
            'asistencias': asistencias.get(e['id'], {})
        })

    return Response({
        'curso':   {'id': cpm.curso_id,   'nombre_curso': cpm.curso.nombre_curso},
        'materia': {'id': cpm.materia_id, 'nombre': cpm.materia.nombre},
        'fechas': fechas,
        'estudiantes': estudiantes_payload
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upsert_asistencia_cpm(request, cpm_id: int):
    """
    Body:
    {
      "fecha": "2025-08-21",
      "estudiante_id": 12,
      "estado": "Presente" | "Tarde" | "Ausente"
    }
    """
    cpm = get_object_or_404(CursoProfesorMateria, id=cpm_id)
    fecha = request.data.get('fecha')
    estudiante_id = request.data.get('estudiante_id')
    estado = request.data.get('estado')

    if estado not in ('Presente', 'Tarde', 'Ausente'):
        return Response({'detail': 'Estado inválido'}, status=400)
    if not (fecha and estudiante_id):
        return Response({'detail': 'fecha y estudiante_id son requeridos'}, status=400)

    # (opcional) verifica que el estudiante pertenezca al curso del CPM
    get_object_or_404(Estudiante, id=estudiante_id, curso_id=cpm.curso_id)

    obj, created = Asistencia.objects.update_or_create(
        cpm=cpm, estudiante_id=estudiante_id, fecha=fecha,
        defaults={'estado': estado}
    )
    return Response({'id': obj.id, 'created': created}, status=status.HTTP_200_OK)
