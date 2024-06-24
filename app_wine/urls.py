from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Adicionando a importação de settings
from django.conf.urls.static import static  # Adicionando a importação de static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/users/', include('users.urls', namespace='users')),
    path('api/v1/wines/', include('wines.urls', namespace='wines')),
    path('api/v1/suppliers/', include('suppliers.urls', namespace='suppliers')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
