# usuarios/views_password_reset.py
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

User = get_user_model()

FRONTEND_RESET_URL = getattr(settings, 'FRONTEND_RESET_URL', 'http://localhost:5173/reset-password')

class PasswordResetRequestAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        value = ser.validated_data['email_or_username'].strip()
        user = User.objects.filter(Q(email__iexact=value) | Q(username__iexact=value)).first()

        # Siempre responder 200 para no filtrar usuarios
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{FRONTEND_RESET_URL}/{uid}/{token}"

            subject = "Restablecer contraseña"
            msg = (
                "Has solicitado restablecer tu contraseña.\n\n"
                f"Ingresa al siguiente enlace para continuar:\n{link}\n\n"
                "Si no fuiste tú, ignora este mensaje."
            )
            send_mail(subject, msg, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [user.email], fail_silently=True)

        return Response({"detail": "Si el usuario existe, se enviará un correo con instrucciones."}, status=200)


class PasswordResetConfirmAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        uid = ser.validated_data['uid']
        token = ser.validated_data['token']
        new_password = ser.validated_data['new_password']

        try:
            uid_int = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_int)
        except Exception:
            return Response({"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Contraseña restablecida correctamente."}, status=200)
