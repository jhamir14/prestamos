#!/bin/bash

# Script de despliegue final para Render.com
echo "🚀 Iniciando despliegue en Render..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar que Django esté instalado
echo "🔍 Verificando Django..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Verificar configuración
echo "✅ Verificando configuración..."
python manage.py check --deploy

# Crear superusuario si no existe (solo en desarrollo)
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
"

echo "🎉 Despliegue completado exitosamente!"
