from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.api.views import CustomTokenObtainPairView, UserViewSet, PasswordResetView, PasswordResetConfirmView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', include(router.urls)),
]
