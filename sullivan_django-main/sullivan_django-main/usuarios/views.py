# usuarios/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserRegistrationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAdministrador

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAdministrador])   # Solo un administrador puede crear usuarios
def register_user(request):
    # Antes este endpoint era público y aceptaba el campo "rol": cualquiera podía crearse una
    # cuenta de Administrador. Ahora exige un token de administrador (los usuarios se crean
    # desde el panel: Personas -> Agregar persona).
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Guardamos el nuevo usuario
            return Response({"message": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
