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
from .escala import etiqueta, promedio as promediar_niveles

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


def escala_desempeno(nivel):
    """
    Texto del desempeño a partir del código de nivel (1, 2 o 3):
      1 -> Deficiente · 2 -> Aceptable · 3 -> Sobresaliente · None -> Sin evaluar
    (Antes era la escala numérica BAJO/BÁSICO/ALTO/SUPERIOR; ver academico/escala.py.)
    """
    return etiqueta(nivel)


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
        # Las notas son NIVELES cualitativos (1 Deficiente, 2 Aceptable, 3 Sobresaliente).
        # Se promedian con la misma función que usa la planilla del profesor (escala.py):
        # media de los códigos -> se redondea al nivel más cercano.
        # Ya no se usa el "peso" de las actividades: con tres niveles no tiene sentido ponderar,
        # y antes las actividades sin peso se ignoraban en silencio cuando otras sí lo tenían.
        # Las actividades sin evaluar (None) no cuentan en el promedio.
        promedio_final, nivel_final = promediar_niveles([ae.calificacion for ae in entregas])

        # Si existe una nota final consolidada manualmente por el docente (NotaMateriaPeriodo),
        # esta tiene prioridad sobre el cálculo automático
        observacion_docente = ''
        if NotaMateriaPeriodo:
            nmp = NotaMateriaPeriodo.objects.filter(estudiante=estudiante, cpm=cpm, periodo=periodo).first()
            if nmp:
                observacion_docente = nmp.observacion_docente or ''
                if nmp.promedio is not None:
                    promedio_final, nivel_final = promediar_niveles([nmp.promedio])

        desempeno = escala_desempeno(nivel_final)

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
            'nivel_codigo': nivel_final,   # 1, 2, 3 o None: el front lo usa para el color del nivel
            'inasistencias': faltas,
            'observacion_docente': observacion_docente,
            'logros': logros,
        })

    # Resumen general del periodo: promedio cualitativo de los niveles de todas las materias.
    # Se calcula aquí (misma función de escala.py) para que el front no repita la cuenta.
    _, nivel_general = promediar_niveles([m['nivel_codigo'] for m in materias_resultado])
    inasistencias_total = sum(m['inasistencias'] for m in materias_resultado)

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
        'desempeno_general': escala_desempeno(nivel_general),
        'nivel_general': nivel_general,
        'inasistencias_total': inasistencias_total,
        'observaciones_generales': '',
    }
