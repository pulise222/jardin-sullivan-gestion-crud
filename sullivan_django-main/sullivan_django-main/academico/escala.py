"""
================================================================================
ESCALA DE EVALUACIÓN CUALITATIVA - PROYECTO SULLIVAN
================================================================================
A los niños del jardín no se les califica con números de 0 a 5 sino con tres
niveles:  Deficiente · Aceptable · Sobresaliente.

¿Cómo se "promedian" palabras? Guardamos cada nivel como un CÓDIGO (1, 2 o 3) en
la columna `calificacion` que ya existía, así la base de datos no cambia de forma.
Para promediar:  media de los códigos  ->  se redondea al nivel más cercano.

    1 = Deficiente      2 = Aceptable      3 = Sobresaliente

    Ejemplo: Sobresaliente (3) + Aceptable (2) -> media 2.5 -> redondea hacia
    arriba -> Sobresaliente.

Toda la lógica de la escala vive SOLO en este archivo: el boletín, la planilla
del profesor y la vista del acudiente la usan de aquí, para que nunca haya
dos cálculos distintos.
================================================================================
"""
from decimal import Decimal, ROUND_HALF_UP

NIVELES = {
    1: 'Deficiente',
    2: 'Aceptable',
    3: 'Sobresaliente',
}
CODIGOS_VALIDOS = tuple(NIVELES.keys())
SIN_EVALUAR = 'Sin evaluar'


def codigo_de(valor):
    """Convierte lo que venga (Decimal, int, '2.0', None) en un código 1-3, o None."""
    if valor is None or valor == '':
        return None
    try:
        return int(Decimal(str(valor)))
    except Exception:
        return None


def etiqueta(valor):
    """Código -> texto. Si no hay nota devuelve 'Sin evaluar'."""
    return NIVELES.get(codigo_de(valor), SIN_EVALUAR)


def promedio(codigos):
    """
    Media de una lista de códigos (ignora los None = actividades sin evaluar).
    Devuelve (media con 1 decimal, código del nivel redondeado), o (None, None) si no hay notas.
    """
    validos = [c for c in (codigo_de(x) for x in codigos) if c in NIVELES]
    if not validos:
        return None, None
    media = Decimal(sum(validos)) / Decimal(len(validos))
    # ROUND_HALF_UP: 2.5 sube a 3 (con el redondeo normal de Python sería 2)
    nivel = int(media.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    return float(media.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)), nivel
