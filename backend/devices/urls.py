from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, DeviceSaleViewSet, DeviceInstallmentViewSet

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'sales', DeviceSaleViewSet)
router.register(r'installments', DeviceInstallmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
