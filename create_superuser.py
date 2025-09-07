#!/usr/bin/env python
"""
Script para crear superusuario en Django
Ejecuta este script en Render para crear un superusuario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    """Crear superusuario si no existe"""
    User = get_user_model()
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("ℹ️ Ya existe un superusuario en la base de datos")
        return
    
    # Crear superusuario
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Superusuario creado exitosamente!")
        print("📧 Usuario: admin")
        print("📧 Email: admin@example.com")
        print("🔑 Contraseña: admin123")
        print("🌐 Accede al admin en: https://tu-dominio.onrender.com/admin/")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

def list_users():
    """Listar usuarios existentes"""
    User = get_user_model()
    users = User.objects.all()
    
    print(f"👥 Usuarios en la base de datos: {users.count()}")
    for user in users:
        status = "👑 Superusuario" if user.is_superuser else "👤 Usuario normal"
        print(f"   - {user.username} ({user.email}) - {status}")

if __name__ == '__main__':
    print("🚀 Creando superusuario en Django...")
    print("=" * 50)
    
    # Listar usuarios existentes
    list_users()
    print()
    
    # Crear superusuario
    create_superuser()
    
    print("=" * 50)
    print("✅ Proceso completado!")
