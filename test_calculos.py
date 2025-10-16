from prestamos.models import Cliente, Prestamo
from datetime import datetime, timedelta

print("🧪 PROBANDO CÁLCULOS DE CUOTAS AUTOMÁTICAS")
print("=" * 50)

# Crear un cliente de prueba si no existe
cliente, created = Cliente.objects.get_or_create(
    nombre="Cliente Prueba",
    defaults={
        'telefono': '999999999',
        'direccion': 'Dirección de prueba'
    }
)

if created:
    print(f"✅ Cliente de prueba creado: {cliente.nombre}")
else:
    print(f"📋 Usando cliente existente: {cliente.nombre}")

# Escenario 1: Préstamo semanal de 500 soles por 15 días
print("\n📊 ESCENARIO 1: Préstamo semanal de 500 soles por 15 días")
fecha_prestamo = datetime.now().date()
fecha_vencimiento = fecha_prestamo + timedelta(days=15)

prestamo1 = Prestamo(
    cliente=cliente,
    monto=500,
    fecha_prestamo=fecha_prestamo,
    fecha_vencimiento=fecha_vencimiento,
    forma_pago='semanal'
)

print(f"   Monto base: S/ {prestamo1.monto}")
print(f"   Interés (quincenal): S/ {prestamo1.monto_interes} ({prestamo1.porcentaje_interes_total * 100:.0f}%)")
print(f"   Monto total: S/ {prestamo1.monto_total}")
print(f"   Días totales: {prestamo1.dias_totales}")
print(f"   Número de cuotas: {prestamo1.numero_cuotas}")
print(f"   Monto por cuota: S/ {prestamo1.monto_por_cuota}")

# Escenario 2: Préstamo diario de 500 soles por 15 días
print("\n📊 ESCENARIO 2: Préstamo diario de 500 soles por 15 días")
prestamo2 = Prestamo(
    cliente=cliente,
    monto=500,
    fecha_prestamo=fecha_prestamo,
    fecha_vencimiento=fecha_vencimiento,
    forma_pago='diario'
)

print(f"   Monto base: S/ {prestamo2.monto}")
print(f"   Interés (quincenal): S/ {prestamo2.monto_interes} ({prestamo2.porcentaje_interes_total * 100:.0f}%)")
print(f"   Monto total: S/ {prestamo2.monto_total}")
print(f"   Días totales: {prestamo2.dias_totales}")
print(f"   Número de cuotas: {prestamo2.numero_cuotas}")
print(f"   Monto por cuota: S/ {prestamo2.monto_por_cuota}")

print("\n✅ VERIFICACIÓN DE CÁLCULOS")
print("=" * 30)

# Verificar escenario 1 (ejemplo del usuario)
expected_total_1 = 500 + (500 * 0.10)  # 550, 1 quincena
expected_cuotas_1 = 3  # 15 días / 7 = ~2.14, redondeado hacia arriba = 3
expected_monto_cuota_1 = expected_total_1 / expected_cuotas_1  # 200

print(f"Escenario 1 - Esperado: {expected_cuotas_1} cuotas de S/ {expected_monto_cuota_1:.2f}")
print(f"Escenario 1 - Calculado: {prestamo1.numero_cuotas} cuotas de S/ {prestamo1.monto_por_cuota:.2f}")

print("\n🎉 ¡Pruebas completadas!")