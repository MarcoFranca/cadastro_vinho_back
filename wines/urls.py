from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wines.api.viewsets import WineViewSet, MovimentoEstoqueViewSet, ExportExcelView, ImportExcelView

app_name = 'wines'

router = DefaultRouter()
router.register(r'wines', WineViewSet)
router.register(r'movimentos', MovimentoEstoqueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('export/', ExportExcelView.as_view(), name='export-excel'),
    path('import/', ImportExcelView.as_view(), name='import-excel'),
]
