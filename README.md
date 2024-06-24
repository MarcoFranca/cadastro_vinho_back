# Documentação do Backend da Aplicação VinoManager

## Tecnologias Utilizadas

- **Django**: Framework web para o desenvolvimento do backend.
- **Django Rest Framework (DRF)**: Utilizado para criar a API RESTful.
- **Django Allauth**: Utilizado para autenticação via redes sociais (Google).
- **Django Simple JWT**: Utilizado para autenticação baseada em tokens JWT.
- **PostgreSQL**: Banco de dados utilizado.

## Configuração

### `settings.py`

#### Principais Configurações

- Uso de variáveis de ambiente para configurações sensíveis.
- Configuração do `Django Allauth` para autenticação via Google.
- Configuração do `Django Simple JWT` para autenticação JWT.
- Definição do modelo de usuário customizado (`CustomUser`).

### Exemplo de Configuração do `settings.py`

```python
from pathlib import Path
import os
import environ
from datetime import timedelta
```
# Diretório Base
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de Ambiente
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Chave Secreta e Debug
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# Hosts Permitidos
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-production-url.com",
]

# Aplicativos Instalados
```json
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wines',
    'users',
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework_simplejwt',
    'corsheaders',
]
```

# Middleware
```json
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]
```

# Templates
```python
ROOT_URLCONF = 'app_wine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app_wine.wsgi.application'
```

# Banco de Dados
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}
```
# Autenticação
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```
# Configurações do JWT
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

```
# Configurações do Django Allauth
```python
SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_ADAPTER = 'users.adapters.MySocialAccountAdapter'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': 'your-google-client-id',
            'secret': 'your-google-client-secret',
            'key': ''
        }
    }
}

SOCIALACCOUNT_REDIRECT_URL = '/'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
```
# Internacionalização
```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

# Arquivos Estáticos e de Mídia
```python

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
# Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```
# Configurações Adicionais
```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```
## Rotas e URLs
urls.py no Projeto Principal
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/users/', include('users.urls', namespace='users')),
    path('api/v1/wines/', include('wines.urls', namespace='wines')),
]
```

urls.py no App users

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.api.views import CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
```
## Views
views.py no App users
```python

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .models import CustomUser
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
```
## Serializers
serializers.py no App users
```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging
from users.models import CustomUser

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        logger.debug(f"Attempting to authenticate user: {username}")

        user = authenticate(username=username, password=password)

        if user is None:
            logger.error(f"Authentication failed for user: {username}")
            raise serializers.ValidationError("No active account found with the given credentials")

        if not user.is_active:
            logger.error(f"Inactive user: {username}")
            raise serializers.ValidationError("User account is disabled")

        data = super().validate(attrs)
        data['username'] = user.username
        logger.debug(f"Authenticated user: {user.username}")
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        logger.debug(f"User created: {user.username}")
        return user
```
## Endpoints
### Criação de Novo Usuário
URL: POST /api/v1/users/users/

**Exemplo de Requisição:**

```json
{
  "username": "novo_usuario",
  "email": "novo_usuario@example.com",
  "password": "senha_secreta"
}
```
### Login (Obtenção de Token JWT)
URL: POST /api/v1/users/token/

Exemplo de Requisição:

```json
{
  "username": "novo_usuario",
  "password": "senha_secreta"
}
```
Resposta Esperada:

```json
{
  "refresh": "token_refresh",
  "access": "token_access"
}
```
## Atualização do Token JWT (Refresh Token)
URL: POST /api/v1/users/token/refresh/
Exemplo de Requisição:

```json
{
  "refresh": "token_refresh"
}
```
Resposta Esperada:

```json
{
  "access": "novo_token_access"
}
```
## Obter Perfil do Usuário
URL: GET /api/v1/users/users/profile/

Cabeçalho de Autenticação:

```makefile
Authorization: Bearer token_access
```
Resposta Esperada:

```json
{
  "id": 1,
  "username": "novo_usuario",
  "email": "novo_usuario@example.com"
}
```
Recuperação de Senha
URL: POST /api/v1/users/users/reset_password/ (a ser implementado)

Exemplo de Requisição:

```json
{
  "email": "novo_usuario@example.com"
}
```
### Autenticação via Google
URL para Login via Google: GET /accounts/google/login/

URL de Callback do Google: Configurada na console de desenvolvedor do Google

## Integração com Frontend (Next.js)
Para integrar com o frontend em Next.js, utilize as URLs fornecidas acima para criar novos usuários, fazer login, atualizar tokens e gerenciar o perfil. Configure o Next.js para lidar com a autenticação via Google.








