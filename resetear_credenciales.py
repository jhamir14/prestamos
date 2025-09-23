#!/usr/bin/env python
"""
Script para resetear credenciales del superusuario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')
django.setup()

from django.contrib.auth import get_user_model

def resetear_credenciales():
    """Resetear credenciales del superusuario"""
    User = get_user_model()
    
    print("🔧 Reseteando credenciales del superusuario...")
    print("=" * 50)
    
    # Credenciales que queremos establecer
    nuevo_username = 'jhamir14'
    nuevo_email = 'admin@example.com'
    nueva_password = 'jhamirquispe'
    
    try:
        # Buscar superusuario existente
        superusuarios = User.objects.filter(is_superuser=True)
        
        if superusuarios.exists():
            # Actualizar el primer superusuario encontrado
            user = superusuarios.first()
            print(f"📧 Superusuario encontrado: {user.username}")
            
            # Actualizar credenciales
            user.username = nuevo_username
            user.email = nuevo_email
            user.set_password(nueva_password)
            user.save()
            
            print("✅ Credenciales actualizadas exitosamente!")
            print(f"👤 Usuario: {nuevo_username}")
            print(f"📧 Email: {nuevo_email}")
            print(f"🔑 Contraseña: {nueva_password}")
            
        else:
            # Crear nuevo superusuario
            print("⚠️ No se encontró superusuario. Creando uno nuevo...")
            user = User.objects.create_superuser(
                username=nuevo_username,
                email=nuevo_email,
                password=nueva_password
            )
            print("✅ Superusuario creado exitosamente!")
            print(f"👤 Usuario: {nuevo_username}")
            print(f"📧 Email: {nuevo_email}")
            print(f"🔑 Contraseña: {nueva_password}")
            
    except Exception as e:
        print(f"❌ Error reseteando credenciales: {e}")

def eliminar_usuarios_duplicados():
    """Eliminar usuarios duplicados o innecesarios"""
    User = get_user_model()
    
    print("\n🧹 Limpiando usuarios duplicados...")
    print("=" * 50)
    
    try:
        # Buscar usuarios admin antiguos
        usuarios_admin = User.objects.filter(username='admin')
        if usuarios_admin.exists():
            print(f"🗑️ Eliminando {usuarios_admin.count()} usuario(s) 'admin' antiguos...")
            usuarios_admin.delete()
            print("✅ Usuarios 'admin' eliminados")
        
        # Verificar que solo quede un superusuario
        superusuarios = User.objects.filter(is_superuser=True)
        print(f"👑 Superusuarios restantes: {superusuarios.count()}")
        
        for user in superusuarios:
            print(f"   - {user.username} ({user.email})")
            
    except Exception as e:
        print(f"❌ Error limpiando usuarios: {e}")

if __name__ == '__main__':
    print("🚀 Reseteando credenciales del sistema...")
    print("=" * 60)
    
    resetear_credenciales()
    eliminar_usuarios_duplicados()
    
    print("=" * 60)
    print("✅ Proceso completado!")
    print()
    print("🌐 Ahora puedes acceder con:")
    print("   Usuario: jhamir14")
    print("   Contraseña: jhamirquispe")
    print("   URL: https://prestamos-jrnd.onrender.com/signin/")