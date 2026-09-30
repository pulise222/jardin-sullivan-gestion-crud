# 🌞 Jardín Sullivan · Sistema de gestión

Aplicación web para administrar un jardín infantil: estudiantes, cursos, profesores, asistencia,
actividades, **evaluación de los niños** y **boletines por trimestre** para las familias.

> **Demo en vivo:** https://pulise222.github.io/jardin-sullivan-demo/
> Se puede recorrer completa, sin instalar nada (los datos son de ejemplo).
> Cuentas de prueba: `admin`, `profesor` y `acudiente`, todas con la contraseña `Demo2026*`.

## ¿Qué problema resuelve?

Un jardín infantil suele llevar la asistencia, las tareas y las notas en papel o en hojas de cálculo sueltas,
y las familias no ven cómo va su hijo hasta que reciben el boletín. Este sistema centraliza todo:
el administrador organiza el jardín, los profesores registran el día a día y las familias consultan
el avance de sus hijos cuando quieran.

## Funciones por rol

| Rol | Qué puede hacer |
| --- | --- |
| **Administrador** | Gestiona estudiantes (con importación masiva desde Excel/CSV), personas, materias, asignaciones profesor-curso-materia y eventos. Vincula acudientes con sus hijos. |
| **Profesor** | Ve sus cursos, toma asistencia, crea actividades y **evalúa por materia y trimestre** en una planilla, y consulta los eventos del jardín. |
| **Acudiente** | Ve los datos y las actividades de cada hijo (puede adjuntar evidencias), consulta el **boletín de cada trimestre** con el resumen del año, e imprime o guarda el boletín en PDF. |

## Una decisión de diseño pensada para el dominio

A los niños pequeños **no se les califica con números**. El sistema usa tres niveles:
**Deficiente · Aceptable · Sobresaliente**.

Para poder promediarlos, cada nivel se guarda como un código (1, 2 o 3) y el promedio es la media de esos
códigos redondeada al nivel más cercano (Sobresaliente + Aceptable = 2,5 → Sobresaliente).
Toda esa lógica vive en **un solo archivo** del backend (`academico/escala.py`), que usan la planilla
del profesor y el boletín, y el backend **rechaza** cualquier valor fuera de la escala.

## Tecnologías

| Capa | Herramientas |
| --- | --- |
| **Front-end** | React 19, Vite, React Router, Redux Toolkit + RTK Query, Formik + Yup, CSS propio (sistema de diseño con temas por rol) |
| **Back-end** | Django 4.2, Django REST Framework, JWT (SimpleJWT), documentación Swagger (drf-yasg) |
| **Base de datos** | MySQL (XAMPP) o SQLite |
| **Calidad** | 15 pruebas automáticas del backend, despliegue de la demo con GitHub Actions |

## Estructura del repositorio

```
sullivan_django-main/sullivan_django-main/   → API (Django)
  academico/    periodos, boletín y la escala de evaluación (escala.py)
  actividades/  actividades y evaluaciones
  clases/       asistencia
  personas/     personas, asignaciones y el comando cargar_datos_demo
  estudiantes/, cursos/, materias/, eventos/, usuarios/, asignaciones/
react-sulley-master/react-sulley-master/     → Interfaz (React)
  src/components/views/   Home, Login, Admin, Profe, Acudiente
  src/styles/panel.css    sistema de diseño compartido por los tres paneles
```

## Cómo correrlo en tu computador

Necesitas **Python 3.11+** y **Node 20+**.

**1. Backend (API)**

```bash
cd sullivan_django-main/sullivan_django-main
python -m venv venv
venv\Scripts\activate            # en Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_datos_demo   # crea las cuentas y datos de ejemplo
python manage.py runserver           # http://127.0.0.1:8000
```

Por defecto usa **SQLite**, así que no necesitas instalar nada más. Para usar **MySQL** (XAMPP), crea la base
de datos y define `USE_MYSQL=1` y `DB_NAME` antes de ejecutar (ver `.env.example`).

**2. Front-end**

```bash
cd react-sulley-master/react-sulley-master
npm install
npm run dev                          # http://localhost:5173
```

Entra con `admin`, `profesor` o `acudiente` (contraseña `Demo2026*`).

## Pruebas

```bash
cd sullivan_django-main/sullivan_django-main
python manage.py test
```

Cubren la escala y sus promedios, el rechazo de notas fuera de la escala, la planilla filtrada por materia
y trimestre, el cálculo del boletín, los permisos del registro de usuarios y el comando de datos de ejemplo.

## Seguridad

- Autenticación con **JWT** y permisos por rol en los endpoints sensibles.
- Crear usuarios es una acción **solo de administrador**.
- **CORS** limitado al front configurado; `ALLOWED_HOSTS` limitado a la máquina local por defecto.
- La clave secreta y el modo `DEBUG` se leen de variables de entorno (ver `.env.example`); Django se niega a
  arrancar en producción con la clave del repositorio.

## Autor

Proyecto de portafolio desarrollado por **Juan Sebastián Pulido Bojaca** durante su formación tecnológica en el **SENA**:
interfaz y sistema de diseño, evaluación cualitativa, boletín por trimestre, seguridad, pruebas y demo.
