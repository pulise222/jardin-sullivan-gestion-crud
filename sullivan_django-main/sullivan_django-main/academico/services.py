"""
================================================================================
SERVICIO DE CÁLCULO DE CALIFICACIONES Y BOLETINES - PROYECTO SULLIVAN
================================================================================
Este archivo contiene la lógica matemática y de negocio para:
  1. Calcular el promedio ponderado o simple de notas por materia y período.
  2. Determinar la escala de desempeño nacional (BAJO, BÁSICO, ALTO, SUPERIOR).
  3. Contabilizar fallas de asistencia (inasistencias) durante el período.
  4. Consolidar los logros académicos alcanzados por el alumno.
  5. Ensamblar la estructura final de datos del Boletín de Calificaciones.
================================================================================
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.db.models import Q

from actividades.models import Actividad, ActividadEstudiante
from personas.models import CursoProfesorMateria
from estudiantes.models import Estudiante
from cursos.models import Curso
from .models import Periodo, Logro

# Importación segura de Asistencia (si el módulo clases está activo)
try:
    from clases.models import Asistencia
except ImportError:
    Asistencia = None

try:
    from .models import NotaMateriaPeriodo
except ImportError:
    NotaMateriaPeriodo = None


def _redondear_1d(valor):
    """
    Redondea una calificación numérica a exactamente 1 decimal con criterio estándar:
    si el segundo decimal es >= 5 redondea hacia arriba (ej. 3.46 -> 3.5, 3.44 -> 3.4).
    """
    if valor is None:
        return None
    return float(Decimal(str(valor)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def escala_desempeno(nota):
    """
    Clasifica la nota numérica según la escala institucional de evaluación en Colombia:
      - 0.0 a 2.9: DESEMPEÑO BAJO    (No alcanza los objetivos mínimos)
      - 3.0 a 3.9: DESEMPEÑO BÁSICO   (Alcanza los objetivos con apoyo)
      - 4.0 a 4.5: DESEMPEÑO ALTO    (Buen nivel de comprensión y trabajo)
      - 4.6 a 5.0: DESEMPEÑO SUPERIOR(Supera ampliamente las metas)
    """
    if nota is None:
        return 'SIN NOTA'
    if nota < 3.0:
        return 'BAJO'
    elif nota < 4.0:
        return 'BÁSICO'
    elif nota <= 4.5:
        return 'ALTO'
    return 'SUPERIOR'


def calcular_boletin_estudiante_periodo(curso_id: int, periodo: Periodo, estudiante_id: int):
    """
    Calcula la planilla detallada de un estudiante para un período escolar.

    Paso a paso del algoritmo:
      1. Obtiene el estudiante y verifica que pertenezca al curso solicitado.
      2. Busca todas las materias asignadas a ese curso (vía CursoProfesorMateria).
      3. Para cada materia:
         a) Busca las actividades asociadas al período (por clave foránea 'periodo'
            o por rango de fechas entre fecha_inicio y fecha_fin del período).
         b) Obtiene las notas que el estudiante sacó en cada una de esas actividades.
         c) Calcula el promedio:
            - Si las actividades tienen 'peso' (porcentajes), calcula el promedio ponderado.
            - Si no tienen peso, calcula la media aritmética simple.
         d) Cuenta las inasistencias en el período.
         e) Agrega los logros e indicadores pedagógicos configurados.
      4. Retorna el diccionario consolidado listo para visualización web o exportación a PDF.
    """
    curso = Curso.objects.get(pk=curso_id)
    estudiante = Estudiante.objects.get(pk=estudiante_id, curso=curso)

    # Materias asignadas al curso con sus respectivos docentes
    cpms = (
        CursoProfesorMateria.objects
        .select_related('materia', 'persona')
        .filter(curso=curso)
    )

    materias_resultado = []

    for cpm in cpms:
        # Filtro de actividades del período:
        # Consideramos una actividad válida si está explícitamente vinculada al período
        # O si su fecha de asignación está comprendida entre el inicio y fin del período.
        filtro_actividades = Q(asignada_por=cpm)
        if periodo.fecha_inicio and periodo.fecha_fin:
            filtro_actividades &= (
                Q(periodo=periodo) |
                (Q(fecha__gte=periodo.fecha_inicio) & Q(fecha__lte=periodo.fecha_fin))
            )
        else:
            filtro_actividades &= Q(periodo=periodo)

        actividades = list(
            Actividad.objects.filter(filtro_actividades).values('id', 'titulo', 'fecha', 'peso')
        )

        # Entregas y notas del estudiante para las actividades encontradas
        act_ids = [a['id'] for a in actividades]
        entregas = (
            ActividadEstudiante.objects
            .filter(estudiante=estudiante, actividad_id__in=act_ids)
            .select_related('actividad')
        )

        # ----------------------------------------------------------------------
        # CÁLCULO DE PROMEDIO DE NOTAS
        # ----------------------------------------------------------------------
        suma_ponderada = Decimal('0.0')
        suma_pesos = Decimal('0.0')
        notas_simples = []

        for ae in entregas:
            if ae.calificacion is not None:
                nota = Decimal(str(ae.calificacion))
                notas_simples.append(float(nota))

                # Si la actividad tiene configurado un porcentaje/peso
                peso = ae.actividad.peso
                if peso and peso > 0:
                    suma_ponderada += nota * Decimal(str(peso))
                    suma_pesos += Decimal(str(peso))

        # Determinar promedio final de la materia:
        if suma_pesos > 0:
            # Promedio ponderado por porcentajes
            promedio_calculado = float(suma_ponderada / suma_pesos)
        elif notas_simples:
            # Promedio aritmético simple si no hay pesos asignados
            promedio_calculado = sum(notas_simples) / len(notas_simples)
        else:
            promedio_calculado = None

        # Si existe una nota final consolidada manualmente por el docente (NotaMateriaPeriodo),
        # esta tiene prioridad sobre el cálculo automático
        observacion_docente = ''
        if NotaMateriaPeriodo:
            nmp = NotaMateriaPeriodo.objects.filter(estudiante=estudiante, cpm=cpm, periodo=periodo).first()
            if nmp:
                observacion_docente = nmp.observacion_docente or ''
                if nmp.promedio is not None:
                    promedio_calculado = float(nmp.promedio)

        promedio_final = _redondear_1d(promedio_calculado)
        desempeno = escala_desempeno(promedio_final)

        # ----------------------------------------------------------------------
        # CÁLCULO DE INASISTENCIAS (FALTAS)
        # ----------------------------------------------------------------------
        faltas = 0
        if Asistencia is not None and periodo.fecha_inicio and periodo.fecha_fin:
            faltas = Asistencia.objects.filter(
                estudiante=estudiante,
                cpm=cpm,
                fecha__gte=periodo.fecha_inicio,
                fecha__lte=periodo.fecha_fin,
                estado__iexact='Ausente'
            ).count()

        # ----------------------------------------------------------------------
        # LOGROS Y DESCRIPTORES PEDAGÓGICOS
        # ----------------------------------------------------------------------
        logros_qs = Logro.objects.filter(cpm=cpm, periodo=periodo).order_by('orden')
        logros = [{'orden': lg.orden, 'descripcion': lg.descripcion} for lg in logros_qs]

        materias_resultado.append({
            'materia_nombre': cpm.materia.nombre,
            'profesor': f"{cpm.persona.nombre} {cpm.persona.apellido}",
            'promedio': promedio_final,
            'desempeno': desempeno,
            'inasistencias': faltas,
            'observacion_docente': observacion_docente,
            'logros': logros,
        })

    # Estructura del boletín consolidado
    return {
        'anio': periodo.anio,
        'generado_el': date.today().isoformat(),
        'curso': {
            'id': curso.id,
            'nombre_curso': curso.nombre_curso,
        },
        'periodo': {
            'id': periodo.id,
            'anio': periodo.anio,
            'numero': periodo.numero,
            'nombre': periodo.nombre,
            'fecha_inicio': periodo.fecha_inicio.isoformat() if periodo.fecha_inicio else None,
            'fecha_fin': periodo.fecha_fin.isoformat() if periodo.fecha_fin else None,
            'activo': periodo.activo,
        },
        'estudiante': {
            'id': estudiante.id,
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'tipo_documento': estudiante.tipo_documento,
            'numero_documento': estudiante.numero_documento,
        },
        'materias': materias_resultado,
        'observaciones_generales': '',
    }
