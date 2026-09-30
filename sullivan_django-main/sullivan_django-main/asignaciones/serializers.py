# asignaciones/serializers.py
from rest_framework import serializers
from personas.models import CursoProfesorMateria, Persona
from cursos.models import Curso
from materias.models import Materia

class CursoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'nombre_curso']

class MateriaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ['id', 'nombre']

class PersonaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'nombre', 'apellido']

class CursoProfesorMateriaSerializer(serializers.ModelSerializer):
    # lectura (anidados)
    curso   = CursoMiniSerializer(read_only=True)
    materia = MateriaMiniSerializer(read_only=True)
    persona = PersonaMiniSerializer(read_only=True)

    # escritura (ids)
    curso_id   = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(), source='curso', write_only=True
    )
    materia_id = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), source='materia', write_only=True
    )
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), source='persona', write_only=True
    )

    class Meta:
        model  = CursoProfesorMateria
        fields = [
            'id',
            'curso', 'materia', 'persona',    # read
            'curso_id', 'materia_id', 'persona_id',  # write
        ]
