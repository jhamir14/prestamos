#!/usr/bin/env python
"""
Script específico para migrar datos de SQLite a PostgreSQL
Usa este script si tienes datos existentes en SQLite que quieres transferir
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')

def export_from_sqlite():
    """Exportar datos desde SQLite"""
    print("📤 Exportando datos desde SQLite...")
    
    # Usar SQLite para exportar
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    django.setup()
    
    from prestamos.models import Cliente, Prestamo, CuotaPago
    
    # Exportar Clientes
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
    
    print(f"✅ Exportados {len(clientes_data)} clientes")
    
    # Exportar Prestamos
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
    
    print(f"✅ Exportados {len(prestamos_data)} préstamos")
    
    # Exportar CuotasPago
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
    
    print(f"✅ Exportadas {len(cuotas_data)} cuotas")
    
    return len(clientes_data), len(prestamos_data), len(cuotas_data)

def import_to_postgres():
    """Importar datos a PostgreSQL"""
    print("📥 Importando datos a PostgreSQL...")
    
    # Usar PostgreSQL para importar
    os.environ['DATABASE_URL'] = 'postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos'
    django.setup()
    
    from prestamos.models import Cliente, Prestamo, CuotaPago
    from decimal import Decimal
    from datetime import datetime
    
    # Limpiar datos existentes
    print("🧹 Limpiando datos existentes...")
    CuotaPago.objects.all().delete()
    Prestamo.objects.all().delete()
    Cliente.objects.all().delete()
    
    # Importar Clientes
    with open('clientes_export.json', 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
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
    
    print(f"✅ Importados {len(clientes_data)} clientes")
    
    # Importar Prestamos
    with open('prestamos_export.json', 'r', encoding='utf-8') as f:
        prestamos_data = json.load(f)
    
    for prestamo_data in prestamos_data:
        Prestamo.objects.create(
            id=prestamo_data['id'],
            cliente_id=prestamo_data['cliente_id'],
            monto=Decimal(prestamo_data['monto']),
            fecha_prestamo=datetime.fromisoformat(prestamo_data['fecha_prestamo']).date(),
            fecha_vencimiento=datetime.fromisoformat(prestamo_data['fecha_vencimiento']).date(),
            forma_pago=prestamo_data['forma_pago'],
            estado=prestamo_data['estado'],
        )
    
    print(f"✅ Importados {len(prestamos_data)} préstamos")
    
    # Importar CuotasPago
    with open('cuotas_export.json', 'r', encoding='utf-8') as f:
        cuotas_data = json.load(f)
    
    for cuota_data in cuotas_data:
        CuotaPago.objects.create(
            id=cuota_data['id'],
            prestamo_id=cuota_data['prestamo_id'],
            fecha_pago=datetime.fromisoformat(cuota_data['fecha_pago']).date(),
            monto=Decimal(cuota_data['monto']),
            pagada=cuota_data['pagada'],
            fecha_pagada=datetime.fromisoformat(cuota_data['fecha_pagada']).date() if cuota_data['fecha_pagada'] else None,
            tipo_cuota=cuota_data['tipo_cuota'],
        )
    
    print(f"✅ Importadas {len(cuotas_data)} cuotas")

def main():
    print("🔄 Iniciando migración de SQLite a PostgreSQL...")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Uso: python migrate_sqlite_to_postgres.py [export|import]")
        print("  export: Exportar datos desde SQLite")
        print("  import: Importar datos a PostgreSQL")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'export':
        try:
            clientes, prestamos, cuotas = export_from_sqlite()
            print(f"\n✅ Exportación completada:")
            print(f"   - {clientes} clientes")
            print(f"   - {prestamos} préstamos")
            print(f"   - {cuotas} cuotas")
            print("\n📁 Archivos creados:")
            print("   - clientes_export.json")
            print("   - prestamos_export.json")
            print("   - cuotas_export.json")
        except Exception as e:
            print(f"❌ Error en exportación: {e}")
            sys.exit(1)
    
    elif command == 'import':
        try:
            # Verificar que existen los archivos de exportación
            required_files = ['clientes_export.json', 'prestamos_export.json', 'cuotas_export.json']
            for file in required_files:
                if not os.path.exists(file):
                    print(f"❌ Archivo requerido no encontrado: {file}")
                    print("Ejecuta primero: python migrate_sqlite_to_postgres.py export")
                    sys.exit(1)
            
            import_to_postgres()
            print(f"\n✅ Importación completada exitosamente!")
            print("🎉 Tu base de datos PostgreSQL ahora tiene todos los datos de SQLite")
        except Exception as e:
            print(f"❌ Error en importación: {e}")
            sys.exit(1)
    
    else:
        print("❌ Comando inválido. Usa 'export' o 'import'")
        sys.exit(1)

if __name__ == '__main__':
    main()
