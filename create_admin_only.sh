#!/usr/bin/env bash
# Script para crear solo el superusuario
set -e

echo "🔧 Creando superusuario en Django..."

# Crear superusuario
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='jhamir14').exists():
    User.objects.create_superuser('jhamir14', 'admin@example.com', 'jhamirquispe')
    print('✅ Superusuario creado exitosamente!')
    print('👤 Usuario: jhamir14')
    print('🔑 Contraseña: jhamirquispe')
    print('🌐 Accede en: https://prestamos-jrnd.onrender.com/admin/')
else:
    print('ℹ️ El superusuario ya existe')
"

echo "✅ Proceso completado!"
