from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MotoViewSet

router = DefaultRouter()
router.register(r'motos', MotoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
