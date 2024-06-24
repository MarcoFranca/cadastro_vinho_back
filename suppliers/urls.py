from django.urls import path, include
from rest_framework.routers import DefaultRouter
from suppliers.api.viewsets import SupplierViewSet

app_name = 'suppliers'

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
