#!/usr/bin/env python
"""
Script para probar los cálculos de cuotas automáticas
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prestamos.settings')
django.setup()

from prestamos.models import Cliente, Prestamo

def probar_escenarios():
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
    print(f"   Interés (20%): S/ {prestamo1.monto * 0.20}")
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
    print(f"   Interés (20%): S/ {prestamo2.monto * 0.20}")
    print(f"   Monto total: S/ {prestamo2.monto_total}")
    print(f"   Días totales: {prestamo2.dias_totales}")
    print(f"   Número de cuotas: {prestamo2.numero_cuotas}")
    print(f"   Monto por cuota: S/ {prestamo2.monto_por_cuota}")
    
    # Escenario 3: Préstamo semanal de 1000 soles por 30 días
    print("\n📊 ESCENARIO 3: Préstamo semanal de 1000 soles por 30 días")
    fecha_vencimiento_30 = fecha_prestamo + timedelta(days=30)
    
    prestamo3 = Prestamo(
        cliente=cliente,
        monto=1000,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento_30,
        forma_pago='semanal'
    )
    
    print(f"   Monto base: S/ {prestamo3.monto}")
    print(f"   Interés (20%): S/ {prestamo3.monto * 0.20}")
    print(f"   Monto total: S/ {prestamo3.monto_total}")
    print(f"   Días totales: {prestamo3.dias_totales}")
    print(f"   Número de cuotas: {prestamo3.numero_cuotas}")
    print(f"   Monto por cuota: S/ {prestamo3.monto_por_cuota}")
    
    # Escenario 4: Préstamo diario de 1000 soles por 30 días
    print("\n📊 ESCENARIO 4: Préstamo diario de 1000 soles por 30 días")
    prestamo4 = Prestamo(
        cliente=cliente,
        monto=1000,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento_30,
        forma_pago='diario'
    )
    
    print(f"   Monto base: S/ {prestamo4.monto}")
    print(f"   Interés (20%): S/ {prestamo4.monto * 0.20}")
    print(f"   Monto total: S/ {prestamo4.monto_total}")
    print(f"   Días totales: {prestamo4.dias_totales}")
    print(f"   Número de cuotas: {prestamo4.numero_cuotas}")
    print(f"   Monto por cuota: S/ {prestamo4.monto_por_cuota}")
    
    # Verificar que los cálculos sean correctos
    print("\n✅ VERIFICACIÓN DE CÁLCULOS")
    print("=" * 30)
    
    # Verificar escenario 1 (ejemplo del usuario)
    expected_total_1 = 500 + (500 * 0.20)  # 600
    expected_cuotas_1 = 3  # 15 días / 7 = ~2.14, redondeado hacia arriba = 3
    expected_monto_cuota_1 = expected_total_1 / expected_cuotas_1  # 200
    
    print(f"Escenario 1 - Esperado: {expected_cuotas_1} cuotas de S/ {expected_monto_cuota_1:.2f}")
    print(f"Escenario 1 - Calculado: {prestamo1.numero_cuotas} cuotas de S/ {prestamo1.monto_por_cuota:.2f}")
    
    # Verificar escenario 2
    # Para días laborables en 15 días (excluyendo domingos)
    dias_laborables = 0
    fecha_actual = fecha_prestamo + timedelta(days=1)
    while fecha_actual <= fecha_vencimiento:
        if fecha_actual.weekday() != 6:  # 6 = domingo
            dias_laborables += 1
        fecha_actual += timedelta(days=1)
    
    expected_monto_cuota_2 = expected_total_1 / dias_laborables
    
    print(f"Escenario 2 - Esperado: {dias_laborables} cuotas de S/ {expected_monto_cuota_2:.2f}")
    print(f"Escenario 2 - Calculado: {prestamo2.numero_cuotas} cuotas de S/ {prestamo2.monto_por_cuota:.2f}")
    
    print("\n🎉 ¡Pruebas completadas!")

if __name__ == "__main__":
    probar_escenarios()