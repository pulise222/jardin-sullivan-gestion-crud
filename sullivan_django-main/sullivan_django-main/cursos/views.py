from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from estudiantes.models import Estudiante
from estudiantes.serializers import EstudianteSerializer
from .models import Curso
from .serializers import CursoSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])    
def estudiantes_del_curso(request, curso_id):
    estudiantes = Estudiante.objects.filter(curso_id=curso_id)
    serializer = EstudianteSerializer(estudiantes, many=True)
    return Response(serializer.data)