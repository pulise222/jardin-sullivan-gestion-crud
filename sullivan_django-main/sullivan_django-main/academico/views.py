# academico/views.py
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import shutil
import pdfkit

from .services import calcular_boletin_estudiante_periodo
from .models import Periodo


def _resolver_periodo(periodo_param, request):
    """
    Si viene ?anio=YYYY y 'periodo_param' es el número (1..4), resuelve por (anio, numero).
    Si no, intenta como PK.
    """
    anio_q = request.GET.get('anio')
    if anio_q:
        return get_object_or_404(Periodo, anio=int(anio_q), numero=int(periodo_param))
    return get_object_or_404(Periodo, pk=int(periodo_param))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def boletin_curso_json(request, curso_id: int, periodo_id: int):
    periodo = _resolver_periodo(periodo_id, request)
    est_id = request.GET.get('estudiante_id')
    if not est_id:
        return JsonResponse({'detail': 'Falta estudiante_id'}, status=400)
    data = calcular_boletin_estudiante_periodo(curso_id, periodo, int(est_id))
    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def boletin_curso_pdf(request, curso_id: int, periodo_id: int):
    # 1) Resolver periodo por ?anio=YYYY o por PK
    periodo = _resolver_periodo(periodo_id, request)

    # 2) Requerir estudiante_id
    est_id = request.GET.get('estudiante_id')
    if not est_id:
        return Response({'detail': 'Falta estudiante_id'}, status=400)

    # 3) Calcular data del boletín (un estudiante)
    data = calcular_boletin_estudiante_periodo(curso_id, periodo, int(est_id))

    # 4) Render HTML
    html = render_to_string('boletin/curso_periodo.html', {'data': data})

    # 5) Localizar wkhtmltopdf
    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', None) or shutil.which('wkhtmltopdf')
    if not cmd:
        return Response(
            {"detail": "wkhtmltopdf no está instalado o no se encontró en PATH."},
            status=503
        )
    config = pdfkit.configuration(wkhtmltopdf=cmd)
    options = {
        'page-size': 'A4',
        'margin-top': '18mm',
        'margin-right': '15mm',
        'margin-bottom': '20mm',
        'margin-left': '15mm',
        'encoding': 'UTF-8',
        # Si en el template usas file:// para logo/css locales:
        'enable-local-file-access': None,
        'quiet': '',
    }

    # 6) PDF en memoria
    pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)

    # 7) Respuesta como attachment con nombre bonito
    filename = (
        f"boletin_{data['estudiante']['nombre']}_{data['estudiante']['apellido']}"
        f"_P{data['periodo']['numero']}_{data['anio']}.pdf"
    ).replace(' ', '_')
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contexto_academico(request):
    """
    Devuelve:
      - anio_actual: año calendario actual
      - periodo_actual: el periodo “en curso” (el siguiente al último que ya terminó)
      - periodos_disponibles: lista de números de periodos cerrados (< periodo_actual)
    Si no hay filas en Periodo para el año actual, hace un fallback por meses.
    """
    hoy = timezone.now().date()
    anio_actual = hoy.year

    qs = Periodo.objects.filter(anio=anio_actual).order_by('numero')
    if not qs.exists():
        # Fallback: divide el año por trimestres/cuatrimestres según tu política.
        # Ejemplo simple: 4 periodos => cada 3 meses
        periodo_actual = ((hoy.month - 1) // 3) + 1
        periodos_disponibles = list(range(1, max(1, periodo_actual)))
        return Response({
            'anio_actual': anio_actual,
            'periodo_actual': periodo_actual,
            'periodos_disponibles': periodos_disponibles,
        })

    # “Actual” = siguiente al último que ya terminó (o el primero si ninguno terminó)
    ultimo_cerrado = qs.filter(fecha_fin__lt=hoy).order_by('-numero').first()
    if ultimo_cerrado:
        periodo_actual = min(ultimo_cerrado.numero + 1, qs.last().numero)
    else:
        periodo_actual = qs.first().numero

    periodos_disponibles = [n for n in qs.values_list('numero', flat=True) if n < periodo_actual]

    return Response({
        'anio_actual': anio_actual,
        'periodo_actual': periodo_actual,
        'periodos_disponibles': periodos_disponibles,
    })