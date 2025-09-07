#!/usr/bin/env python
"""
Script para probar la conexión a PostgreSQL
Ejecuta este script para verificar que la conexión a tu base de datos funciona
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
os.environ['DATABASE_URL'] = 'postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos'

django.setup()

from django.db import connection
from django.core.management import call_command

def test_database_connection():
    """Prueba la conexión a la base de datos PostgreSQL"""
    print("🔍 Probando conexión a PostgreSQL...")
    
    try:
        # Probar conexión básica
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexión exitosa!")
            print(f"📊 Versión de PostgreSQL: {version[0]}")
            
        # Probar que las tablas existen
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"📋 Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def run_migrations():
    """Ejecutar migraciones de Django"""
    print("\n🔄 Ejecutando migraciones...")
    
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migraciones completadas exitosamente!")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def create_superuser():
    """Crear superusuario si no existe"""
    print("\n👤 Verificando superusuario...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("⚠️  No se encontró superusuario. Creando uno...")
            call_command('createsuperuser', interactive=False, username='admin', email='admin@example.com')
            print("✅ Superusuario creado: admin")
        else:
            print("✅ Superusuario ya existe")
            
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

def test_models():
    """Probar que los modelos funcionan correctamente"""
    print("\n🧪 Probando modelos...")
    
    try:
        from prestamos.models import Cliente, Prestamo, CuotaPago
        
        # Contar registros existentes
        clientes_count = Cliente.objects.count()
        prestamos_count = Prestamo.objects.count()
        cuotas_count = CuotaPago.objects.count()
        
        print(f"📊 Registros en la base de datos:")
        print(f"   - Clientes: {clientes_count}")
        print(f"   - Préstamos: {prestamos_count}")
        print(f"   - Cuotas: {cuotas_count}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando modelos: {e}")
        return False

def main():
    print("🚀 Iniciando pruebas de PostgreSQL...")
    print("=" * 50)
    
    # Probar conexión
    if not test_database_connection():
        print("\n❌ No se pudo conectar a la base de datos. Verifica la configuración.")
        sys.exit(1)
    
    # Ejecutar migraciones
    if not run_migrations():
        print("\n❌ Error en las migraciones.")
        sys.exit(1)
    
    # Crear superusuario
    if not create_superuser():
        print("\n❌ Error creando superusuario.")
        sys.exit(1)
    
    # Probar modelos
    if not test_models():
        print("\n❌ Error probando modelos.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("✅ Tu aplicación Django está lista para usar PostgreSQL")
    print("\n📝 Próximos pasos:")
    print("1. Despliega tu aplicación en Render")
    print("2. Verifica que funcione correctamente")
    print("3. Si tienes datos en SQLite, usa el script de migración")

if __name__ == '__main__':
    main()
