#!/usr/bin/env bash
# Script para ejecutar migraciones de base de datos
# Útil para ejecutar manualmente después del despliegue

echo "Ejecutando migraciones de base de datos..."

# Aplicar migraciones
python manage.py migrate

# Crear superusuario si no existe
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('El superusuario ya existe')
"

echo "Migraciones completadas."
