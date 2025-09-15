"""
URL configuration for gestion_prestamos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from prestamos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('index/', views.index, name='index'),
    path('prestamos-diarios/', views.prestamos_diarios, name='prestamos_diarios'),
    path('prestamos-semanales/', views.prestamos_semanales, name='prestamos_semanales'),
    path('crear/prestamo/', views.crear_prestamo, name='crear_prestamo'),
    path('registrar-cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('registrar-prestamo/', views.registrar_prestamo, name='registrar_prestamo'),
    path('calendario-pagos/<int:prestamo_id>/', views.calendario_pagos, name='calendario_pagos'),
    path('descargar-calendario/<int:prestamo_id>/', views.descargar_calendario_pdf, name='descargar_calendario_pdf'),
    path('eliminar-prestamo/<int:prestamo_id>/', views.eliminar_prestamo, name='eliminar_prestamo'),
    path('cancelar-prestamo/<int:prestamo_id>/', views.cancelar_prestamo, name='cancelar_prestamo'),
    path('marcar-cuota-pagada/<int:cuota_id>/', views.marcar_cuota_pagada, name='marcar_cuota_pagada'),
    path('reporte-pagos/', views.reporte_pagos, name='reporte_pagos'),
    path('api/buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
]
