# usuarios/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from usuarios.models import Usuario
from django.core.exceptions import ValidationError

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # No hace falta declarar campos extras: usa username/password por defecto

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Se requieren 'username' y 'password'.")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password
        )
        print(user, "usuario")
        if not user:
            raise serializers.ValidationError("Credenciales incorrectas.")

        # Ejecuta la validación estándar (genera access y refresh)
        data = super().validate(attrs)

        # Añade datos de usuario al payload
        data["usuario"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
        }
        return data
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'password2', 'rol']

    def validate_password(self, value):
        # Validar que la contraseña tenga al menos 8 caracteres
        if len(value) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    def validate(self, data):
        # Validar que las contraseñas coincidan
        if data['password'] != data['password2']:
            raise ValidationError("Las contraseñas no coinciden.")
        return data

    def create(self, validated_data):
        # Elimina 'password2' antes de crear el usuario
        validated_data.pop('password2')
        user = Usuario.objects.create_user(**validated_data)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)