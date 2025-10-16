import os
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')

import django
django.setup()

from prestamos.models import Cliente, Prestamo


def seed():
    cliente, created = Cliente.objects.get_or_create(
        nombre='Cliente Demo',
        defaults={
            'email': 'demo@example.com',
            'telefono': '999999999',
            'direccion': 'Av. Demo 123',
            'ciudad': 'Lima',
            'pais': 'Perú',
        }
    )

    # Crear préstamo de ejemplo con 45 días (3 quincenas)
    fecha_prestamo = date.today()
    fecha_vencimiento = fecha_prestamo + timedelta(days=45)

    prestamo = Prestamo.objects.create(
        cliente=cliente,
        monto=Decimal('1000.00'),
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento,
        forma_pago='diario',
    )
    prestamo.generar_cuotas()

    print('✅ Datos de ejemplo insertados:')
    print(f"Cliente: {cliente.nombre}")
    print(f"Prestamo: S/ {prestamo.monto} | Quincenas: {prestamo.quincenas_totales} | Interés: {prestamo.porcentaje_interes_total * 100}% | Total: {prestamo.monto_total}")
    print(f"Cuotas generadas: {prestamo.cuotas.count()}")


if __name__ == '__main__':
    seed()