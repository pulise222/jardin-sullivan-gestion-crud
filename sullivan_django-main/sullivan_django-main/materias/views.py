from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Materia
from .serializers import MateriaSerializer

class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
