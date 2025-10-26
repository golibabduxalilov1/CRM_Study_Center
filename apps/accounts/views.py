from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import User, AllowedEmail, OTPCode
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    OTPVerificationSerializer,
    AllowedEmailSerializer,
    UserSerializer,
)
from apps.core.permissions import IsSuperAdmin, CanManageAllowlist


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "Ro'yxatdan o'tish muvaffaqiyatli", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]

        code = "".join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(seconds=settings.OTP_TTL)

        OTPCode.objects.create(email=user.email, code=code, expires_at=expires_at)

        send_mail(
            "Training CRM - OTP Kod",
            f"Sizning OTP kodingiz: {code}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "OTP kod emailingizga yuborildi", "email": user.email}
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = OTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        otp = serializer.validated_data["otp"]
        user = User.objects.get(email=otp.email)

        otp.used = True
        otp.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Tizimdan muvaffaqiyatli chiqdingiz"})
    except Exception as e:
        return Response({"error": "Token yaroqsiz"}, status=status.HTTP_400_BAD_REQUEST)
