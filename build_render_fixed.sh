#!/bin/bash

# Script de despliegue mejorado para Render.com
echo "🚀 Iniciando despliegue mejorado para Render..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements_render.txt

# Verificar configuración de Django
echo "🔍 Verificando configuración de Django..."
python manage.py check --deploy

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Verificar que la aplicación funciona
echo "✅ Verificando aplicación..."
python manage.py check

echo "🎉 Despliegue completado exitosamente!"
