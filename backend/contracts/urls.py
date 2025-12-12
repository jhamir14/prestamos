from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoMotoViewSet, CuotaContratoViewSet

router = DefaultRouter()
router.register(r'contracts', ContratoMotoViewSet)
router.register(r'installments', CuotaContratoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
