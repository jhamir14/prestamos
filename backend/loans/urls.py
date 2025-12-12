from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrestamoViewSet, CuotaPrestamoViewSet

router = DefaultRouter()
router.register(r'loans', PrestamoViewSet)
router.register(r'installments', CuotaPrestamoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
