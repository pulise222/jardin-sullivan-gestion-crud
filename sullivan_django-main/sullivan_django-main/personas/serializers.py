from rest_framework import serializers
from .models import Persona, CursoProfesorMateria
from cursos.models import Curso
from materias.models import Materia
from usuarios.models import Usuario

class UsuarioInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'rol', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},  # lo igualaremos a email si no viene
        }

class PersonaSerializer(serializers.ModelSerializer):
    usuario = UsuarioInlineSerializer()
    foto_url = serializers.SerializerMethodField()
    class Meta:
        model = Persona
        fields = [
            'id',
            'nombre',
            'apellido',
            'telefono',
            'tipo_documento',
            'numero_documento',
            'direccion',
            'fecha_nacimiento',
            'usuario',
            'foto_url'
        ]
    def create(self, validated_data):
        user_data = validated_data.pop('usuario')

        email = user_data.get('email')
        username = user_data.get('username') or email
        rol = user_data.get('rol')
        password = validated_data.get('numero_documento')

        user = Usuario(username=username, email=email, rol=rol)
        if password:
            user.set_password(password)
        else:
            # si no te mandan password, puedes dejarlo inutilizable o generar uno
            user.set_unusable_password()
            # o: user.set_password(Usuario.objects.make_random_password())
        user.save()

        persona = Persona.objects.create(usuario=user, **validated_data)
        return persona

    def update(self, instance, validated_data):
        user_data = validated_data.pop('usuario', None)
        if user_data:
            user = instance.usuario
            user.email = user_data.get('email', user.email)
            user.username = user_data.get('username', user.username) or user.email
            if 'rol' in user_data:
                user.rol = user_data['rol']
            if 'password' in user_data and user_data['password']:
                user.set_password(user_data['password'])
            user.save()

        return super().update(instance, validated_data)

    def get_foto_url(self, obj):
        if not obj.foto:
            return None
        request = self.context.get('request')
        try:
            url= obj.foto.url if obj.foto else None
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None
        
class CargaEstudiantesSerializer(serializers.Serializer):
    file = serializers.FileField()