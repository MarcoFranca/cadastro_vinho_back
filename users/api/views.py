from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, PasswordResetSerializer, SetNewPasswordSerializer
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save()
        logger.debug(f"User created: {user.username}")

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password(self, request):
        # Implement reset password logic
        pass


class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f"http://localhost:3000/reset-password-confirm/{uid}/{token}/"
            email_subject = 'Password Reset Requested'
            email_body = render_to_string('password_reset_email.html', {
                'reset_link': reset_link,
                'user': user,
            })

            email_message = EmailMultiAlternatives(
                email_subject,
                email_body,
                'your-email@gmail.com',
                [user.email]
            )
            email_message.attach_alternative(email_body, "text/html")
            email_message.send()

            return Response({'message': 'Password reset link sent successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            logger.error(f"User with email {email} does not exist")
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request, uidb64, token):
        logger.debug(f"Password reset request received with uidb64: {uidb64} and token: {token}")
        logger.debug(f"Request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            logger.debug(f"User found: {user.username}")

            token_generator = PasswordResetTokenGenerator()
            if not token_generator.check_token(user, token):
                logger.error(f"Invalid token for user: {user.username}")
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['password'])
            user.save()
            logger.debug(f"Password reset successful for user: {user.username}")

            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            logger.error(f"Invalid token or user")
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)
