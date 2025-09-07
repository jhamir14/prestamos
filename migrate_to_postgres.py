#!/usr/bin/env python
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this script after setting up your PostgreSQL database on Render
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

from prestamos.models import Cliente, Prestamo, CuotaPago
import json

def export_sqlite_data():
    """Export data from SQLite database to JSON files"""
    print("Exporting data from SQLite...")
    
    # Export Clientes
    clientes_data = []
    for cliente in Cliente.objects.all():
        clientes_data.append({
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'ciudad': cliente.ciudad,
            'pais': cliente.pais,
        })
    
    with open('clientes_export.json', 'w', encoding='utf-8') as f:
        json.dump(clientes_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(clientes_data)} clientes")
    
    # Export Prestamos
    prestamos_data = []
    for prestamo in Prestamo.objects.all():
        prestamos_data.append({
            'id': prestamo.id,
            'cliente_id': prestamo.cliente_id,
            'monto': str(prestamo.monto),
            'fecha_prestamo': prestamo.fecha_prestamo.isoformat(),
            'fecha_vencimiento': prestamo.fecha_vencimiento.isoformat(),
            'forma_pago': prestamo.forma_pago,
            'estado': prestamo.estado,
        })
    
    with open('prestamos_export.json', 'w', encoding='utf-8') as f:
        json.dump(prestamos_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(prestamos_data)} prestamos")
    
    # Export CuotasPago
    cuotas_data = []
    for cuota in CuotaPago.objects.all():
        cuotas_data.append({
            'id': cuota.id,
            'prestamo_id': cuota.prestamo_id,
            'fecha_pago': cuota.fecha_pago.isoformat(),
            'monto': str(cuota.monto),
            'pagada': cuota.pagada,
            'fecha_pagada': cuota.fecha_pagada.isoformat() if cuota.fecha_pagada else None,
            'tipo_cuota': cuota.tipo_cuota,
        })
    
    with open('cuotas_export.json', 'w', encoding='utf-8') as f:
        json.dump(cuotas_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(cuotas_data)} cuotas")
    print("Data export completed!")

def import_to_postgres():
    """Import data to PostgreSQL database"""
    print("Importing data to PostgreSQL...")
    
    # Load clientes
    with open('clientes_export.json', 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
    # Clear existing data
    Cliente.objects.all().delete()
    
    for cliente_data in clientes_data:
        Cliente.objects.create(
            id=cliente_data['id'],
            nombre=cliente_data['nombre'],
            email=cliente_data['email'],
            telefono=cliente_data['telefono'],
            direccion=cliente_data['direccion'],
            ciudad=cliente_data['ciudad'],
            pais=cliente_data['pais'],
        )
    
    print(f"Imported {len(clientes_data)} clientes")
    
    # Load prestamos
    with open('prestamos_export.json', 'r', encoding='utf-8') as f:
        prestamos_data = json.load(f)
    
    Prestamo.objects.all().delete()
    
    for prestamo_data in prestamos_data:
        Prestamo.objects.create(
            id=prestamo_data['id'],
            cliente_id=prestamo_data['cliente_id'],
            monto=prestamo_data['monto'],
            fecha_prestamo=prestamo_data['fecha_prestamo'],
            fecha_vencimiento=prestamo_data['fecha_vencimiento'],
            forma_pago=prestamo_data['forma_pago'],
            estado=prestamo_data['estado'],
        )
    
    print(f"Imported {len(prestamos_data)} prestamos")
    
    # Load cuotas
    with open('cuotas_export.json', 'r', encoding='utf-8') as f:
        cuotas_data = json.load(f)
    
    CuotaPago.objects.all().delete()
    
    for cuota_data in cuotas_data:
        CuotaPago.objects.create(
            id=cuota_data['id'],
            prestamo_id=cuota_data['prestamo_id'],
            fecha_pago=cuota_data['fecha_pago'],
            monto=cuota_data['monto'],
            pagada=cuota_data['pagada'],
            fecha_pagada=cuota_data['fecha_pagada'],
            tipo_cuota=cuota_data['tipo_cuota'],
        )
    
    print(f"Imported {len(cuotas_data)} cuotas")
    print("Data import completed!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py [export|import]")
        print("  export: Export data from SQLite to JSON files")
        print("  import: Import data from JSON files to PostgreSQL")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'export':
        # Switch to SQLite for export
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
        export_sqlite_data()
    elif command == 'import':
        # Use PostgreSQL for import (DATABASE_URL should be set by Render)
        import_to_postgres()
    else:
        print("Invalid command. Use 'export' or 'import'")
        sys.exit(1)

if __name__ == '__main__':
    main()
