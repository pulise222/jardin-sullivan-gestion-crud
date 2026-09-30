"""
================================================================================
VISTAS DE ACTIVIDADES Y CALIFICACIONES - PROYECTO SULLIVAN
================================================================================
Este archivo contiene la lógica para:
  1. Crear y listar tareas/actividades por curso.
  2. Generar automáticamente una fila de entrega para cada estudiante del curso.
  3. Matriz de calificaciones para la planilla de notas del profesor.
  4. Subida y descarga de archivos de entregables (tareas enviadas).
================================================================================
"""

import os
import mimetypes
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.http import FileResponse, Http404
from django.urls import reverse

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Actividad, ActividadEstudiante
from .serializers import (
    ActividadSerializer,
    ActividadCreateSerializer,
    ActividadDetalleSerializer,
    ActividadEntregaSerializer,
)
from datetime import date
from django.db.models import Q
from academico.models import Periodo
from academico.escala import etiqueta, promedio as promediar_niveles, codigo_de, NIVELES
from estudiantes.models import Estudiante
from personas.models import PersonaEstudiante, CursoProfesorMateria


def _actividades_filtradas(request, curso_id):
    """
    Devuelve (queryset, error) con las actividades de un curso, según los parámetros:
      - ?cpm=ID      -> solo las de ESA asignación (curso + materia + profesor). Es lo que usa el
                        panel del profesor: así no se mezclan las materias de un mismo curso.
      - ?todas=1     -> todas las materias del curso.
      - (sin nada)   -> las del profesor autenticado en ese curso.
      - ?periodo=N   -> solo las del periodo N del año (?anio=AAAA, por defecto el actual).
                        Cuenta la actividad si tiene ese periodo asignado o si su fecha cae dentro.
    """
    qs = Actividad.objects.filter(asignada_por__curso_id=curso_id)

    cpm_id = request.query_params.get('cpm')
    if cpm_id:
        qs = qs.filter(asignada_por_id=cpm_id)
    elif request.query_params.get('todas') != '1':
        profesor = getattr(request.user, 'persona', None)
        if profesor is None:
            return None, Response({'detail': 'El usuario autenticado no tiene un perfil de Persona asociado.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = qs.filter(asignada_por__persona=profesor)

    numero = request.query_params.get('periodo')
    if numero:
        anio = int(request.query_params.get('anio') or date.today().year)
        periodo = Periodo.objects.filter(anio=anio, numero=int(numero)).first()
        if periodo is None:
            return qs.none(), None
        qs = qs.filter(Q(periodo=periodo) | Q(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_fin))
    return qs, None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def actividades_por_curso(request, curso_id):
    """
    Lista las actividades de un curso (ver _actividades_filtradas para los filtros ?cpm, ?todas, ?periodo).
    """
    qs, error = _actividades_filtradas(request, curso_id)
    if error:
        return error
    data = ActividadSerializer(qs.order_by('-fecha', '-id'), many=True).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_actividad_en_curso(request, curso_id):
    """
    Crea una nueva actividad para un curso y genera automáticamente
    los registros de entrega vacíos (ActividadEstudiante) para todos los alumnos.

    Body esperado en JSON:
      {
        "titulo": "Taller de pintura dactilar",
        "descripcion": "Realizar dibujo con temperas usando las manos",
        "fecha": "2026-09-25",
        "fecha_entrega": "2026-10-02",
        "asignada_por": 1
      }
    """
    # 1. Validación previa: comprobar que el CPM pertenezca al curso solicitado
    cpm_id = request.data.get('asignada_por') or request.data.get('cpm_id')
    if cpm_id:
        cpm = get_object_or_404(CursoProfesorMateria, pk=cpm_id)
        if cpm.curso_id != curso_id:
            return Response(
                {'detail': f'La asignación docente (cpm_id={cpm_id}) pertenece a otro curso, no al curso {curso_id}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # 2. Validar campos con el serializador
    ser = ActividadCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    actividad = ser.save()

    # Asignar el periodo automáticamente según la fecha de la actividad (si ese periodo existe).
    # Antes quedaba vacío y solo se contaba en el boletín por el rango de fechas.
    periodo = Periodo.objects.filter(fecha_inicio__lte=actividad.fecha, fecha_fin__gte=actividad.fecha).first()
    if periodo:
        actividad.periodo = periodo
        actividad.save(update_fields=['periodo'])

    # 3. Generar la entrega individual para todos los estudiantes matriculados
    # bulk_create(): Optimización clave. En lugar de hacer 30 INSERT individuales,
    # envía una sola consulta SQL agrupada que crea todas las filas de golpe.
    estudiantes = Estudiante.objects.filter(curso_id=curso_id)
    nuevas_entregas = [
        ActividadEstudiante(actividad=actividad, estudiante=e)
        for e in estudiantes
    ]
    ActividadEstudiante.objects.bulk_create(nuevas_entregas)

    return Response(
        ActividadDetalleSerializer(actividad, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_actividad(request, actividad_id):
    """
    Devuelve los datos completos de una actividad específica.
    """
    actividad = get_object_or_404(Actividad, pk=actividad_id)
    return Response(ActividadDetalleSerializer(actividad, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entregas_por_actividad(request, actividad_id):
    """
    Devuelve el listado de alumnos y sus respectivas entregas para una actividad.
    Filtro ?estado=:
      - 'entregadas': Solo los que ya subieron archivo o nota.
      - 'pendientes': Los que aún no han entregado.
      - 'todas': Todos los alumnos del curso.
    """
    estado = (request.query_params.get('estado') or 'todas').lower()
    qs = ActividadEstudiante.objects.select_related('estudiante').filter(actividad_id=actividad_id)

    if estado == 'entregadas':
        qs = qs.exclude(entregado_en__isnull=True)
    elif estado == 'pendientes':
        qs = qs.filter(entregado_en__isnull=True)

    entregas = ActividadEntregaSerializer(qs, many=True, context={'request': request}).data
    return Response(entregas)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def actividad_update_delete(request, actividad_id):
    """
    Modifica parcialmente o elimina una actividad.
    """
    actividad = get_object_or_404(Actividad, pk=actividad_id)

    if request.method == 'DELETE':
        actividad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH: Solo actualizar campos enviados
    campos_permitidos = ['titulo', 'descripcion', 'fecha', 'fecha_entrega', 'peso', 'periodo']
    partial_data = {k: v for k, v in request.data.items() if k in campos_permitidos}

    if not partial_data:
        return Response({'detail': 'No se enviaron campos válidos para actualizar.'}, status=status.HTTP_400_BAD_REQUEST)

    ser = ActividadSerializer(actividad, data=partial_data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_entrega(request, actividad_estudiante_id):
    """
    Califica una entrega o actualiza la fecha de entrega de un estudiante.
    Ejemplo JSON: { "calificacion": 3 }   (1 Deficiente · 2 Aceptable · 3 Sobresaliente)
    Solo se aceptan esos tres niveles (o null para dejarla sin evaluar).
    """
    ae = get_object_or_404(ActividadEstudiante, pk=actividad_estudiante_id)
    campos_actualizables = ['calificacion', 'entregado_en']
    data = {k: v for k, v in request.data.items() if k in campos_actualizables}

    if not data:
        return Response({'detail': 'No se enviaron campos para actualizar.'}, status=status.HTTP_400_BAD_REQUEST)

    ser = ActividadEntregaSerializer(ae, data=data, partial=True, context={'request': request})
    ser.is_valid(raise_exception=True)
    # Evaluar una actividad cuenta como "hecha": si aún no tenía fecha de entrega, se la ponemos.
    # Así los filtros Entregadas/Pendientes del acudiente siguen teniendo sentido.
    extra = {}
    if data.get('calificacion') is not None and ae.entregado_en is None and 'entregado_en' not in data:
        extra['entregado_en'] = now()
    ser.save(**extra)
    return Response(ser.data)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def subir_entregable(request, actividad_estudiante_id):
    """
    Sube el archivo de evidencia o tarea de un estudiante.
    Marca automáticamente la fecha 'entregado_en' con la fecha/hora actual.
    """
    ae = get_object_or_404(ActividadEstudiante, pk=actividad_estudiante_id)
    archivo = request.FILES.get('entregable')
    if not archivo:
        return Response({'detail': "Debe adjuntar un archivo en el campo 'entregable'."}, status=status.HTTP_400_BAD_REQUEST)

    ae.entregable = archivo
    if ae.entregado_en is None:
        ae.entregado_en = now()
    ae.save()

    return Response(ActividadEntregaSerializer(ae, context={'request': request}).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matriz_calificaciones_curso(request, curso_id: int):
    """
    Genera la matriz completa de notas para la planilla del profesor.
    Retorna:
      - 'actividades': Columnas de la planilla (lista de tareas del curso).
      - 'estudiantes': Filas de la planilla (alumnos del curso).
      - 'celdas': Cada evaluación individual que cruza estudiante con actividad.
    Cada estudiante trae además su 'promedio' y su 'nivel' (Deficiente/Aceptable/Sobresaliente),
    calculados AQUÍ con academico/escala.py: es la misma cuenta que usa el boletín.
    Filtros: ?cpm=ID (una materia), ?periodo=N (un periodo), ?todas=1 (ver _actividades_filtradas).
    """
    acts_qs, error = _actividades_filtradas(request, curso_id)
    if error:
        return error

    actividades = list(acts_qs.order_by('fecha', 'id').values('id', 'titulo', 'fecha'))
    estudiantes = list(Estudiante.objects.filter(curso_id=curso_id).order_by('apellido', 'nombre').values('id', 'nombre', 'apellido'))

    # Traer todas las entregas que correspondan a estas actividades
    act_ids = [a['id'] for a in actividades]
    rel_qs = ActividadEstudiante.objects.select_related('actividad', 'estudiante').filter(actividad_id__in=act_ids)

    celdas = []
    codigos_por_estudiante = {}
    for ae in rel_qs:
        url = None
        if ae.entregable:
            try:
                url = ae.entregable.url
            except Exception:
                url = None

        codigo = codigo_de(ae.calificacion)
        codigos_por_estudiante.setdefault(ae.estudiante_id, []).append(codigo)
        celdas.append({
            'actividad_id': ae.actividad_id,
            'estudiante_id': ae.estudiante_id,
            'actividad_estudiante_id': ae.id,
            'calificacion': codigo,   # 1, 2, 3 o None (sin evaluar)
            'entregado_en': (ae.entregado_en.isoformat() if ae.entregado_en else None),
            'entregable_url': url,
        })

    # Promedio cualitativo de cada estudiante en las actividades mostradas
    for est in estudiantes:
        media, nivel = promediar_niveles(codigos_por_estudiante.get(est['id'], []))
        est['promedio'] = media
        est['nivel'] = NIVELES.get(nivel, etiqueta(None))
        est['nivel_codigo'] = nivel

    return Response({
        'actividades': actividades,
        'estudiantes': estudiantes,
        'celdas': celdas,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entregas_por_estudiante(request, estudiante_id: int):
    """
    Devuelve el historial de tareas y entregas de un estudiante.
    Usado principalmente en el portal de Acudientes para revisar las tareas de su hijo.
    """
    estado = (request.query_params.get('estado') or 'todas').lower()

    qs = (ActividadEstudiante.objects
          .select_related('actividad', 'actividad__asignada_por__materia')
          .filter(estudiante_id=estudiante_id))

    if estado == 'pendientes':
        qs = qs.filter(entregado_en__isnull=True)
    elif estado == 'entregadas':
        qs = qs.filter(entregado_en__isnull=False)

    payload = []
    for ae in qs.order_by('-actividad__fecha', '-actividad__id'):
        a = ae.actividad

        preview_url = None
        mime = None
        filename = None

        if ae.entregable:
            try:
                rel_url = ae.entregable.url
                preview_url = request.build_absolute_uri(rel_url)
                path = ae.entregable.path
                mime, _ = mimetypes.guess_type(path)
                filename = os.path.basename(path)
            except Exception:
                pass

        download_url = request.build_absolute_uri(
            reverse('descargar-entregable', args=[ae.id])
        )

        payload.append({
            'id': ae.id,
            'actividad_estudiante_id': ae.id,
            'actividad_id': a.id,
            'materia': a.asignada_por.materia.nombre if a.asignada_por else None,
            'titulo': a.titulo,
            'descripcion': a.descripcion,
            'fecha': a.fecha.isoformat() if a.fecha else None,
            'fecha_entrega': a.fecha_entrega.isoformat() if a.fecha_entrega else None,
            'entregado_en': ae.entregado_en.isoformat() if ae.entregado_en else None,
            'calificacion': codigo_de(ae.calificacion),   # 1, 2, 3 o None
            'nivel': etiqueta(ae.calificacion),           # "Sobresaliente", "Sin evaluar"…
            'entregable_url': preview_url,
            'download_url': download_url,
            'mime': mime,
            'filename': filename,
        })

    return Response(payload)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def descargar_entregable(request, actividad_estudiante_id: int):
    """
    Fuerza la descarga protegida del archivo entregable.
    Seguridad:
      Solo pueden descargar el archivo:
      1. Un superusuario o administrador.
      2. El acudiente asignado al estudiante.
      3. El profesor asignado al curso del estudiante.
    """
    ae = get_object_or_404(ActividadEstudiante, pk=actividad_estudiante_id)

    # Verificación de autorización
    persona = getattr(request.user, 'persona', None)
    autorizado = request.user.is_superuser or request.user.rol == 'Administrador'

    if persona and not autorizado:
        # Verificar si es acudiente del alumno
        if PersonaEstudiante.objects.filter(persona=persona, estudiante=ae.estudiante).exists():
            autorizado = True
        # Verificar si es profesor del curso
        elif CursoProfesorMateria.objects.filter(persona=persona, curso=ae.estudiante.curso).exists():
            autorizado = True

    if not autorizado:
        return Response({'detail': 'No tienes permisos para descargar este archivo.'}, status=status.HTTP_403_FORBIDDEN)

    if not ae.entregable:
        raise Http404('No existe archivo adjunto para esta entrega.')

    path = ae.entregable.path
    mime, _ = mimetypes.guess_type(path)
    filename = os.path.basename(path)

    response = FileResponse(open(path, 'rb'), content_type=mime or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response