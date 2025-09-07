#!/usr/bin/env bash
# Script para crear solo el superusuario
set -e

echo "🔧 Creando superusuario en Django..."

# Crear superusuario
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuario creado exitosamente!')
    print('👤 Usuario: admin')
    print('🔑 Contraseña: admin123')
    print('🌐 Accede en: https://prestamos-jrnd.onrender.com/admin/')
else:
    print('ℹ️ El superusuario ya existe')
"

echo "✅ Proceso completado!"
