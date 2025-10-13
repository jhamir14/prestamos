#!/usr/bin/env python
"""
Script para probar el cálculo de interés progresivo
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prestamos.settings')
django.setup()

from prestamos.models import Prestamo, Cliente

def crear_cliente_prueba():
    """Crear un cliente de prueba"""
    cliente, created = Cliente.objects.get_or_create(
        email='test@example.com',
        defaults={
            'nombre': 'Cliente de Prueba',
            'telefono': '123456789',
            'direccion': 'Dirección de prueba',
            'ciudad': 'Lima',
            'pais': 'Perú'
        }
    )
    return cliente

def probar_escenarios():
    """Probar diferentes escenarios de tiempo"""
    cliente = crear_cliente_prueba()
    fecha_base = date.today()
    
    escenarios = [
        {
            'nombre': 'Préstamo de 15 días (1 quincena)',
            'monto': 500,
            'fecha_prestamo': fecha_base,
            'fecha_vencimiento': fecha_base + timedelta(days=15),
            'esperado_quincenas': 1,
            'esperado_interes_porcentaje': 10
        },
        {
            'nombre': 'Préstamo de 30 días (2 quincenas)',
            'monto': 1000,
            'fecha_prestamo': fecha_base,
            'fecha_vencimiento': fecha_base + timedelta(days=30),
            'esperado_quincenas': 2,
            'esperado_interes_porcentaje': 20
        },
        {
            'nombre': 'Préstamo de 45 días (3 quincenas)',
            'monto': 300,
            'fecha_prestamo': fecha_base,
            'fecha_vencimiento': fecha_base + timedelta(days=45),
            'esperado_quincenas': 3,
            'esperado_interes_porcentaje': 30
        },
        {
            'nombre': 'Préstamo de 60 días (4 quincenas)',
            'monto': 100,
            'fecha_prestamo': fecha_base,
            'fecha_vencimiento': fecha_base + timedelta(days=60),
            'esperado_quincenas': 4,
            'esperado_interes_porcentaje': 40
        }
    ]
    
    print("=== PRUEBAS DE INTERÉS PROGRESIVO ===\n")
    
    for i, escenario in enumerate(escenarios, 1):
        print(f"{i}. {escenario['nombre']}")
        print(f"   Monto: S/ {escenario['monto']}")
        print(f"   Fecha préstamo: {escenario['fecha_prestamo']}")
        print(f"   Fecha vencimiento: {escenario['fecha_vencimiento']}")
        
        # Crear préstamo temporal (sin guardar en BD)
        prestamo = Prestamo(
            cliente=cliente,
            monto=escenario['monto'],
            fecha_prestamo=escenario['fecha_prestamo'],
            fecha_vencimiento=escenario['fecha_vencimiento'],
            forma_pago='semanal'
        )
        
        # Calcular valores
        quincenas_calculadas = prestamo.quincenas_totales
        porcentaje_interes = prestamo.porcentaje_interes_total
        monto_interes = prestamo.monto_interes
        monto_total = prestamo.monto_total

        print(f"   Quincenas calculadas: {quincenas_calculadas}")
        print(f"   Porcentaje de interés: {porcentaje_interes * 100:.0f}%")
        print(f"   Monto de interés: S/ {monto_interes:.2f}")
        print(f"   Monto total: S/ {monto_total:.2f}")
        
        # Verificar resultados
        if quincenas_calculadas == escenario['esperado_quincenas']:
            print("   ✅ Cálculo de quincenas CORRECTO")
        else:
            print(f"   ❌ Cálculo de quincenas INCORRECTO (esperado: {escenario['esperado_quincenas']})")
        
        if abs(porcentaje_interes * 100 - escenario['esperado_interes_porcentaje']) < 0.01:
            print("   ✅ Porcentaje de interés CORRECTO")
        else:
            print(f"   ❌ Porcentaje de interés INCORRECTO (esperado: {escenario['esperado_interes_porcentaje']}%)")
        
        print()

if __name__ == '__main__':
    probar_escenarios()