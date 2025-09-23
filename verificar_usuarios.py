#!/usr/bin/env python
"""
Script para verificar usuarios existentes en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

from django.contrib.auth import get_user_model

def verificar_usuarios():
    """Verificar usuarios existentes en la base de datos"""
    User = get_user_model()
    
    print("🔍 Verificando usuarios en la base de datos...")
    print("=" * 50)
    
    try:
        usuarios = User.objects.all()
        
        if usuarios.exists():
            print(f"👥 Total de usuarios encontrados: {usuarios.count()}")
            print()
            
            for user in usuarios:
                status = "👑 SUPERUSUARIO" if user.is_superuser else "👤 Usuario normal"
                print(f"📧 Usuario: {user.username}")
                print(f"📧 Email: {user.email}")
                print(f"🔑 Estado: {status}")
                print(f"🗓️ Último login: {user.last_login}")
                print(f"🗓️ Fecha creación: {user.date_joined}")
                print("-" * 30)
        else:
            print("⚠️ No se encontraron usuarios en la base de datos")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

def probar_credenciales():
    """Probar diferentes combinaciones de credenciales"""
    User = get_user_model()
    
    print("\n🔐 Probando credenciales comunes...")
    print("=" * 50)
    
    credenciales = [
        ('admin', 'admin123'),
        ('jhamir14', 'jhamirquispe'),
        ('admin', 'jhamirquispe'),
        ('jhamir14', 'admin123')
    ]
    
    for username, password in credenciales:
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                print(f"✅ CREDENCIALES VÁLIDAS: {username} / {password}")
            else:
                print(f"❌ Contraseña incorrecta para: {username}")
        except User.DoesNotExist:
            print(f"⚠️ Usuario no existe: {username}")

if __name__ == '__main__':
    print("🚀 Verificando usuarios y credenciales...")
    print("=" * 60)
    
    verificar_usuarios()
    probar_credenciales()
    
    print("=" * 60)
    print("✅ Verificación completada!")