"""
================================================================================
COMANDO: cargar_datos_demo
================================================================================
Carga datos de EJEMPLO para poder recorrer todo el sistema apenas clonas el repositorio:

    python manage.py migrate
    python manage.py cargar_datos_demo

Crea tres cuentas (contraseña Demo2026*): admin, profesor y acudiente, más cursos, materias,
estudiantes, asignaciones, actividades evaluadas, asistencia, logros, periodos y eventos.
Todos los nombres son inventados. Se puede ejecutar varias veces: no duplica nada.

Evaluación cualitativa: 1 = Deficiente, 2 = Aceptable, 3 = Sobresaliente (ver academico/escala.py).
================================================================================
"""
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from academico.models import Logro, Periodo
from actividades.models import Actividad, ActividadEstudiante
from clases.models import Asistencia
from cursos.models import Curso
from estudiantes.models import Estudiante
from eventos.models import Evento
from materias.models import Materia
from personas.models import CursoProfesorMateria, Persona, PersonaEstudiante
from usuarios.models import Usuario

CLAVE = 'Demo2026*'

# (curso, [(nombre, apellido), ...])
ESTUDIANTES = {
    'Párvulos A': [('Sofía', 'Martínez'), ('Mateo', 'Gómez'), ('Valentina', 'Ríos'), ('Santiago', 'Herrera'), ('Isabella', 'Duarte'), ('Emilio', 'Castaño')],
    'Pre-Jardín': [('Luciana', 'Mejía'), ('Samuel', 'Cárdenas'), ('Mariana', 'Ortiz'), ('Tomás', 'Bermúdez'), ('Antonia', 'Salazar'), ('Julián', 'Pardo')],
    'Jardín': [('Nicolás', 'Vargas'), ('Renata', 'Cuesta'), ('Martín', 'Suárez'), ('Salomé', 'Romero'), ('Dylan', 'Forero'), ('Emma', 'Acosta')],
}

TITULOS = {
    'Arte y Creatividad': ['Dactilopintura con las manos', 'Collage de hojas y flores', 'Mi familia en plastilina', 'Mezclamos colores primarios'],
    'Lectoescritura': ['Reconozco mi nombre', 'Las vocales con canciones', 'Trazos y líneas', 'Letras en arena'],
    'Pensamiento Matemático': ['Cuento con números', 'Clasificamos por colores', 'Contamos hasta diez', 'Figuras geométricas'],
}

LOGROS = {
    'Arte y Creatividad': ['Explora colores y texturas con entusiasmo.', 'Expresa sus ideas mediante el dibujo y la pintura.', 'Comparte materiales con sus compañeros.'],
    'Lectoescritura': ['Reconoce su nombre escrito.', 'Identifica las vocales en canciones y rimas.', 'Realiza trazos controlados con el lápiz.'],
    'Pensamiento Matemático': ['Cuenta objetos hasta diez.', 'Clasifica por color, forma y tamaño.', 'Reconoce figuras geométricas básicas.'],
}


class Command(BaseCommand):
    help = 'Carga datos de ejemplo (cuentas admin, profesor y acudiente con contraseña Demo2026*).'

    def persona(self, username, rol, nombre, apellido, doc):
        usuario, nuevo = Usuario.objects.get_or_create(
            username=username, defaults={'rol': rol, 'email': f'{username}@ejemplo.com'}
        )
        if nuevo:
            usuario.set_password(CLAVE)
            usuario.save()
        persona, _ = Persona.objects.get_or_create(
            usuario=usuario,
            defaults=dict(nombre=nombre, apellido=apellido, telefono='3001234567', tipo_documento='CC',
                          numero_documento=doc, direccion='Calle 10 # 20-30, Bogotá', fecha_nacimiento=date(1985, 5, 15)),
        )
        return persona

    def handle(self, *args, **opciones):
        random.seed(11)
        hoy = date.today()

        # --- Cuentas ---
        self.persona('admin', 'Administrador', 'Laura', 'Gómez', '90000001')
        profesor = self.persona('profesor', 'Profesor', 'Carlos', 'Ramírez', '90000002')
        acudiente = self.persona('acudiente', 'Acudiente', 'Diana', 'Martínez', '90000003')

        # --- Cursos, materias y estudiantes ---
        cursos = {n: Curso.objects.get_or_create(nombre_curso=n, defaults={'descripcion': f'Curso {n}'})[0] for n in ESTUDIANTES}
        materias = {n: Materia.objects.get_or_create(nombre=n)[0] for n in TITULOS}

        doc = 990000000
        estudiantes = {}
        for nombre_curso, lista in ESTUDIANTES.items():
            for i, (nombre, apellido) in enumerate(lista):
                doc += 1
                est, _ = Estudiante.objects.get_or_create(
                    tipo_documento='RC', numero_documento=str(doc),
                    defaults=dict(nombre=nombre, apellido=apellido, curso=cursos[nombre_curso],
                                  fecha_nacimiento=date(hoy.year - 3 - (i % 3), (i % 12) + 1, (i % 27) + 1),
                                  direccion=f'Carrera {10 + i} # 20-30, Bogotá', telefono='3109876543',
                                  correo_electronico=f'familia{doc}@ejemplo.com'),
                )
                estudiantes.setdefault(nombre_curso, []).append(est)

        # --- Hijos de la cuenta "acudiente": dos en Párvulos A y uno en Pre-Jardín ---
        for est in estudiantes['Párvulos A'][:2] + estudiantes['Pre-Jardín'][:1]:
            PersonaEstudiante.objects.get_or_create(persona=acudiente, estudiante=est, defaults={'parentesco': 'Madre'})

        # --- Asignaciones del profesor (curso + materia) ---
        cpms = [
            CursoProfesorMateria.objects.get_or_create(persona=profesor, curso=cursos[c], materia=materias[m])[0]
            for c, m in [('Párvulos A', 'Arte y Creatividad'), ('Párvulos A', 'Lectoescritura'),
                         ('Pre-Jardín', 'Arte y Creatividad'), ('Jardín', 'Pensamiento Matemático')]
        ]

        # --- Periodos: 4 trimestres del año ---
        periodos = []
        for n in range(1, 5):
            inicio = date(hoy.year, (n - 1) * 3 + 1, 1)
            fin = date(hoy.year + (n == 4), (n * 3) % 12 + 1, 1) - timedelta(days=1)
            p, _ = Periodo.objects.get_or_create(
                anio=hoy.year, numero=n,
                defaults=dict(nombre=f'Periodo {n}', fecha_inicio=inicio, fecha_fin=fin, activo=(n == (hoy.month - 1) // 3 + 1)),
            )
            periodos.append(p)

        # --- Actividades evaluadas (trimestres 1 a 3) ---
        pesos = {'fuerte': (0.05, 0.25, 0.70), 'media': (0.12, 0.60, 0.28), 'apoyo': (0.50, 0.40, 0.10)}
        tendencias = ['fuerte', 'media', 'media', 'apoyo', 'fuerte', 'media']

        for cpm in cpms:
            titulos = TITULOS[cpm.materia.nombre]
            for k, periodo in enumerate(periodos[:3]):
                for j, titulo in enumerate(titulos[:3]):
                    fecha = periodo.fecha_inicio + timedelta(days=15 + j * 25)
                    actividad, _ = Actividad.objects.get_or_create(
                        titulo=titulo, asignada_por=cpm, periodo=periodo,
                        defaults=dict(descripcion=f'Actividad de {cpm.materia.nombre.lower()} para trabajar en clase y reforzar en casa.',
                                      fecha=fecha, fecha_entrega=fecha + timedelta(days=5)),
                    )
                    for n, est in enumerate(estudiantes[cpm.curso.nombre_curso]):
                        ae, nuevo = ActividadEstudiante.objects.get_or_create(estudiante=est, actividad=actividad)
                        if not nuevo:
                            continue
                        # La última actividad del trimestre 3 queda a medio evaluar
                        if k == 2 and j == 2 and n % 2 == 1:
                            continue
                        ae.calificacion = Decimal(random.choices([1, 2, 3], weights=pesos[tendencias[n % 6]])[0])
                        ae.entregado_en = timezone.make_aware(datetime.combine(fecha + timedelta(days=1), time(10, 0)))
                        ae.save()

            # Logros por trimestre (los muestra el boletín)
            for periodo in periodos:
                for orden, texto in enumerate(LOGROS[cpm.materia.nombre], start=1):
                    Logro.objects.get_or_create(cpm=cpm, periodo=periodo, orden=orden, defaults={'descripcion': texto})

        # --- Asistencia: últimos 5 días de clase ---
        dias, d = [], hoy
        while len(dias) < 5:
            d -= timedelta(days=1)
            if d.weekday() < 5:
                dias.append(d)
        for cpm in cpms:
            for est in estudiantes[cpm.curso.nombre_curso]:
                for f in dias:
                    r = random.random()
                    Asistencia.objects.get_or_create(
                        cpm=cpm, estudiante=est, fecha=f,
                        defaults={'estado': 'Presente' if r < 0.78 else ('Tarde' if r < 0.9 else 'Ausente')},
                    )

        # --- Eventos próximos (sin imagen) ---
        ahora = timezone.now()
        for dias_faltan, titulo, desc in [
            (12, 'Día de la Familia', 'Una mañana de juegos, música y almuerzo compartido con las familias.'),
            (30, 'Muestra artística', 'Los niños presentan sus trabajos de pintura, plastilina y collage.'),
            (55, 'Charla de nutrición', 'Conversatorio sobre loncheras saludables y hábitos de alimentación.'),
        ]:
            Evento.objects.get_or_create(titulo=titulo, defaults={'descripcion': desc, 'fecha_inicio': ahora + timedelta(days=dias_faltan)})

        self.stdout.write(self.style.SUCCESS(
            f'Datos de ejemplo listos. Cuentas: admin, profesor y acudiente (contraseña {CLAVE}).'
        ))
