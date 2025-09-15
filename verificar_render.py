#!/usr/bin/env python
"""
Script para verificar la configuración de Render
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

def verificar_configuracion():
    """Verifica la configuración de Django"""
    print("🔍 Verificando configuración de Django...")
    
    from django.conf import settings
    from django.db import connection
    from django.core.management import execute_from_command_line
    
    # Verificar configuración básica
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ TIME_ZONE: {settings.TIME_ZONE}")
    print(f"✅ LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
    
    # Verificar base de datos
    print("\n🗄️ Verificando base de datos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False
    
    # Verificar migraciones
    print("\n📋 Verificando migraciones...")
    try:
        from django.core.management import call_command
        call_command('showmigrations', verbosity=0)
        print("✅ Migraciones verificadas")
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False
    
    # Verificar archivos estáticos
    print("\n📁 Verificando archivos estáticos...")
    try:
        from django.contrib.staticfiles.utils import get_files
        from django.contrib.staticfiles.finders import find
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
    except Exception as e:
        print(f"❌ Error en archivos estáticos: {e}")
        return False
    
    # Verificar modelos
    print("\n🏗️ Verificando modelos...")
    try:
        from prestamos.models import Cliente, Prestamo, CuotaPago
        print(f"✅ Cliente: {Cliente.objects.count()} registros")
        print(f"✅ Prestamo: {Prestamo.objects.count()} registros")
        print(f"✅ CuotaPago: {CuotaPago.objects.count()} registros")
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False
    
    return True

def verificar_variables_entorno():
    """Verifica las variables de entorno"""
    print("\n🌍 Verificando variables de entorno...")
    
    variables_importantes = [
        'DATABASE_URL',
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'CSRF_TRUSTED_ORIGINS'
    ]
    
    for var in variables_importantes:
        valor = os.environ.get(var, 'NO CONFIGURADA')
        if var == 'SECRET_KEY' and valor != 'NO CONFIGURADA':
            valor = valor[:10] + '...'  # Ocultar parte de la clave
        print(f"✅ {var}: {valor}")

def main():
    """Función principal"""
    print("🚀 Verificador de Configuración para Render")
    print("=" * 50)
    
    # Verificar variables de entorno
    verificar_variables_entorno()
    
    # Verificar configuración de Django
    if verificar_configuracion():
        print("\n🎉 ¡Configuración verificada exitosamente!")
        print("✅ La aplicación debería funcionar en Render")
    else:
        print("\n❌ Se encontraron problemas en la configuración")
        print("🔧 Revisa los errores anteriores y corrige la configuración")
        sys.exit(1)

if __name__ == '__main__':
    main()
