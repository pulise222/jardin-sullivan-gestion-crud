"""
================================================================================
PRUEBAS AUTOMÁTICAS - EVALUACIÓN CUALITATIVA Y BOLETÍN
================================================================================
Ejecutar todas:   python manage.py test
(sin USE_MYSQL usa SQLite en memoria, así que no toca tus datos)

Qué protegen estas pruebas:
  1. La escala (academico/escala.py): cómo se promedian Deficiente/Aceptable/Sobresaliente.
  2. El backend rechaza notas fuera de la escala (antes aceptaba 7, -2 o 99.9).
  3. La planilla y las actividades se filtran por materia (?cpm) y no se mezclan.
  4. El boletín calcula el desempeño de cada materia y el general.
  5. Solo un administrador puede crear usuarios (antes el registro era público).
Si alguien cambia estas reglas sin querer, una prueba falla y avisa.
================================================================================
"""
from datetime import date

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from academico.escala import codigo_de, etiqueta, promedio
from academico.models import Periodo
from academico.services import calcular_boletin_estudiante_periodo
from actividades.models import Actividad, ActividadEstudiante
from cursos.models import Curso
from estudiantes.models import Estudiante
from materias.models import Materia
from personas.models import CursoProfesorMateria, Persona
from usuarios.models import Usuario


class EscalaTests(SimpleTestCase):
    """La cuenta de la escala: media de los códigos, redondeada al nivel más cercano."""

    def test_etiquetas(self):
        self.assertEqual(etiqueta(1), 'Deficiente')
        self.assertEqual(etiqueta('2.0'), 'Aceptable')
        self.assertEqual(etiqueta(3), 'Sobresaliente')
        self.assertEqual(etiqueta(None), 'Sin evaluar')

    def test_codigo_de_ignora_valores_raros(self):
        self.assertEqual(codigo_de('3.0'), 3)
        self.assertIsNone(codigo_de(''))
        self.assertIsNone(codigo_de('abc'))

    def test_promedio_redondea_hacia_arriba_en_el_punto_medio(self):
        # 3 y 2 -> 2.5 -> sube a Sobresaliente (con el redondeo normal de Python sería 2)
        self.assertEqual(promedio([3, 2]), (2.5, 3))
        self.assertEqual(promedio([1, 2]), (1.5, 2))

    def test_promedio_ignora_lo_no_evaluado(self):
        self.assertEqual(promedio([3, None, 3]), (3.0, 3))
        self.assertEqual(promedio([None, None]), (None, None))
        self.assertEqual(promedio([]), (None, None))


class BaseDatos(TestCase):
    """Datos mínimos compartidos: un curso con dos materias, un profesor y dos niños."""

    @classmethod
    def setUpTestData(cls):
        def persona(username, rol, doc):
            u = Usuario.objects.create_user(username=username, password='Clave-de-prueba-1', rol=rol, email=f'{username}@t.co')
            return Persona.objects.create(
                usuario=u, nombre=username.title(), apellido='Prueba', telefono='3000000000',
                tipo_documento='CC', numero_documento=doc, direccion='Calle 1', fecha_nacimiento=date(1990, 1, 1),
            )

        cls.admin = persona('admin', 'Administrador', '1')
        cls.profe = persona('profe', 'Profesor', '2')
        cls.curso = Curso.objects.create(nombre_curso='Párvulos A', descripcion='x')
        cls.arte = Materia.objects.create(nombre='Arte')
        cls.lecto = Materia.objects.create(nombre='Lectoescritura')
        cls.cpm_arte = CursoProfesorMateria.objects.create(persona=cls.profe, curso=cls.curso, materia=cls.arte)
        cls.cpm_lecto = CursoProfesorMateria.objects.create(persona=cls.profe, curso=cls.curso, materia=cls.lecto)
        cls.ana = Estudiante.objects.create(nombre='Ana', apellido='Uno', curso=cls.curso)
        cls.luis = Estudiante.objects.create(nombre='Luis', apellido='Dos', curso=cls.curso)
        cls.periodo = Periodo.objects.create(anio=2026, numero=1, nombre='Periodo 1', fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 3, 31))

    def actividad(self, cpm, titulo, notas):
        """Crea una actividad del primer trimestre y la evalúa: notas = {estudiante: código}."""
        a = Actividad.objects.create(titulo=titulo, descripcion='d', fecha=date(2026, 2, 10), asignada_por=cpm, periodo=self.periodo)
        for est in (self.ana, self.luis):
            ActividadEstudiante.objects.create(estudiante=est, actividad=a, calificacion=notas.get(est))
        return a

    def api(self, persona):
        c = APIClient()
        c.force_authenticate(user=persona.usuario)
        return c


class ValidacionDeNotasTests(BaseDatos):
    def test_rechaza_notas_fuera_de_la_escala(self):
        a = self.actividad(self.cpm_arte, 'Pintar', {})
        ae = ActividadEstudiante.objects.get(actividad=a, estudiante=self.ana)
        cliente = self.api(self.profe)
        for invalida in (0, 4, 7, -2, 2.5, 99.9):
            r = cliente.patch(f'/actividades/entrega/{ae.id}/', {'calificacion': invalida}, format='json')
            self.assertEqual(r.status_code, 400, f'{invalida} debería rechazarse')

    def test_acepta_niveles_validos_y_marca_la_entrega(self):
        a = self.actividad(self.cpm_arte, 'Pintar', {})
        ae = ActividadEstudiante.objects.get(actividad=a, estudiante=self.ana)
        r = self.api(self.profe).patch(f'/actividades/entrega/{ae.id}/', {'calificacion': 3}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nivel'], 'Sobresaliente')
        ae.refresh_from_db()
        self.assertIsNotNone(ae.entregado_en, 'evaluar debe marcar la actividad como entregada')


class PlanillaPorMateriaTests(BaseDatos):
    def test_la_planilla_no_mezcla_materias(self):
        self.actividad(self.cpm_arte, 'Pintar', {self.ana: 3, self.luis: 1})
        self.actividad(self.cpm_lecto, 'Leer', {self.ana: 1, self.luis: 1})
        cliente = self.api(self.profe)

        arte = cliente.get(f'/actividades/curso/{self.curso.id}/matriz/?cpm={self.cpm_arte.id}').data
        self.assertEqual([a['titulo'] for a in arte['actividades']], ['Pintar'])

        # Sin el filtro ?cpm salen las de todas las materias de ese profesor (comportamiento anterior)
        todas = cliente.get(f'/actividades/curso/{self.curso.id}/matriz/').data
        self.assertEqual(len(todas['actividades']), 2)

    def test_promedio_cualitativo_de_cada_nino(self):
        self.actividad(self.cpm_arte, 'Pintar', {self.ana: 3, self.luis: 1})
        self.actividad(self.cpm_arte, 'Modelar', {self.ana: 2, self.luis: 1})
        datos = self.api(self.profe).get(f'/actividades/curso/{self.curso.id}/matriz/?cpm={self.cpm_arte.id}').data
        por_nombre = {e['nombre']: e for e in datos['estudiantes']}
        self.assertEqual(por_nombre['Ana']['nivel'], 'Sobresaliente')   # (3 + 2) / 2 = 2.5 -> sube
        self.assertEqual(por_nombre['Luis']['nivel'], 'Deficiente')

    def test_filtro_por_periodo(self):
        self.actividad(self.cpm_arte, 'Pintar', {})
        cliente = self.api(self.profe)
        url = f'/actividades/curso/{self.curso.id}/matriz/?cpm={self.cpm_arte.id}&anio=2026'
        self.assertEqual(len(cliente.get(url + '&periodo=1').data['actividades']), 1)
        self.assertEqual(len(cliente.get(url + '&periodo=2').data['actividades']), 0)


class BoletinTests(BaseDatos):
    def test_desempeno_por_materia_y_general(self):
        self.actividad(self.cpm_arte, 'Pintar', {self.ana: 3, self.luis: 2})
        self.actividad(self.cpm_lecto, 'Leer', {self.ana: 2, self.luis: 2})
        b = calcular_boletin_estudiante_periodo(self.curso.id, self.periodo, self.ana.id)
        niveles = {m['materia_nombre']: m['desempeno'] for m in b['materias']}
        self.assertEqual(niveles, {'Arte': 'Sobresaliente', 'Lectoescritura': 'Aceptable'})
        self.assertEqual(b['desempeno_general'], 'Sobresaliente')   # (3 + 2) / 2 = 2.5 -> sube
        self.assertEqual(b['inasistencias_total'], 0)

    def test_materia_sin_evaluaciones_queda_sin_evaluar(self):
        self.actividad(self.cpm_arte, 'Pintar', {})
        b = calcular_boletin_estudiante_periodo(self.curso.id, self.periodo, self.ana.id)
        self.assertTrue(all(m['desempeno'] == 'Sin evaluar' for m in b['materias']))
        self.assertEqual(b['desempeno_general'], 'Sin evaluar')


class RegistroDeUsuariosTests(BaseDatos):
    """El registro solía ser público y aceptaba el rol: cualquiera podía crearse un Administrador."""

    datos = {'username': 'nuevo', 'email': 'n@t.co', 'password': 'Clave-de-prueba-1', 'password2': 'Clave-de-prueba-1', 'rol': 'Administrador'}

    def test_anonimo_no_puede_registrar(self):
        r = APIClient().post('/usuarios/register/', self.datos, format='json')
        self.assertIn(r.status_code, (401, 403))
        self.assertFalse(Usuario.objects.filter(username='nuevo').exists())

    def test_profesor_no_puede_registrar(self):
        r = self.api(self.profe).post('/usuarios/register/', self.datos, format='json')
        self.assertEqual(r.status_code, 403)

    def test_administrador_si_puede(self):
        r = self.api(self.admin).post('/usuarios/register/', self.datos, format='json')
        self.assertEqual(r.status_code, 201)
