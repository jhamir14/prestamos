from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, AdminUserViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'admins', AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]
