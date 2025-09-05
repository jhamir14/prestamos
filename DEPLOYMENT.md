# Guía de Despliegue en Render

Esta guía te ayudará a desplegar tu aplicación Django de gestión de préstamos en Render.

## Archivos de Configuración Creados

### 1. `render.yaml`
Archivo de configuración principal para Render que define:
- Servicio web con Python
- Base de datos PostgreSQL
- Variables de entorno necesarias
- Comandos de construcción y inicio

### 2. `Procfile`
Define el comando para iniciar la aplicación en producción.

### 3. `build.sh`
Script de construcción que:
- Instala dependencias
- Ejecuta migraciones de base de datos
- Crea un superusuario por defecto
- Recolecta archivos estáticos

### 4. `requirements.txt`
Actualizado con dependencias de producción:
- `gunicorn`: Servidor WSGI para producción
- `whitenoise`: Servir archivos estáticos
- `dj-database-url`: Configuración de base de datos
- `psycopg2-binary`: Driver de PostgreSQL

### 5. `env.example`
Archivo de ejemplo con las variables de entorno necesarias.

## Pasos para Desplegar en Render

### 1. Preparar el Repositorio
```bash
# Asegúrate de que todos los archivos estén en tu repositorio
git add .
git commit -m "Configuración para despliegue en Render"
git push origin main
```

### 2. Crear Cuenta en Render
1. Ve a [render.com](https://render.com)
2. Crea una cuenta o inicia sesión
3. Conecta tu cuenta de GitHub

### 3. Crear Nuevo Servicio
1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio `prestamos`

### 4. Configurar el Servicio
- **Name**: `gestion-prestamos` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn gestion_prestamos.wsgi:application`

### 5. Configurar Variables de Entorno
En la sección "Environment Variables" de Render, agrega:

```
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://tu-app.onrender.com
```

### 6. Crear Base de Datos
1. En el dashboard de Render, haz clic en "New +"
2. Selecciona "PostgreSQL"
3. Configura la base de datos:
   - **Name**: `gestion-prestamos-db`
   - **Database**: `gestion_prestamos`
   - **User**: `gestion_prestamos_user`

### 7. Conectar Base de Datos
1. Ve a tu servicio web
2. En "Environment Variables", agrega:
   - **Key**: `DATABASE_URL`
   - **Value**: Copia la "External Database URL" de tu base de datos

### 8. Desplegar
1. Haz clic en "Create Web Service"
2. Render comenzará a construir y desplegar tu aplicación
3. El proceso puede tomar varios minutos

## Acceso a la Aplicación

Una vez desplegada, podrás acceder a tu aplicación en:
- **URL**: `https://tu-app.onrender.com`
- **Admin**: `https://tu-app.onrender.com/admin/`
  - Usuario: `admin`
  - Contraseña: `admin123`

## Configuración de Producción

### Cambiar Contraseña de Admin
1. Accede al admin de Django
2. Ve a "Users" y edita el usuario `admin`
3. Cambia la contraseña por una más segura

### Configuración de Dominio Personalizado
Si tienes un dominio personalizado:
1. Ve a la configuración de tu servicio en Render
2. En "Custom Domains", agrega tu dominio
3. Actualiza las variables de entorno:
   - `ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com`
   - `CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com`

## Monitoreo y Logs

- **Logs**: Ve a tu servicio en Render y haz clic en "Logs"
- **Métricas**: Render proporciona métricas básicas de CPU y memoria
- **Uptime**: Render monitorea automáticamente la disponibilidad de tu aplicación

## Solución de Problemas Comunes

### Error de Archivos Estáticos
Si los archivos CSS/JS no se cargan:
1. Verifica que `collectstatic` se ejecutó correctamente
2. Revisa la configuración de `STATIC_ROOT` en `settings.py`

### Error de Base de Datos
Si hay problemas de conexión:
1. Verifica que `DATABASE_URL` esté configurada correctamente
2. Asegúrate de que la base de datos esté activa

### Error de Migraciones
Si las migraciones fallan:
1. Revisa los logs de construcción
2. Verifica que no haya conflictos en las migraciones

## Costos

- **Plan Gratuito**: Incluye 750 horas de ejecución por mes
- **Base de Datos**: 1GB de almacenamiento gratuito
- **Tráfico**: Ilimitado en el plan gratuito

## Actualizaciones

Para actualizar tu aplicación:
1. Haz push de los cambios a tu repositorio
2. Render detectará automáticamente los cambios
3. Iniciará un nuevo despliegue automáticamente

## Soporte

- **Documentación de Render**: [docs.render.com](https://docs.render.com)
- **Soporte**: Disponible en el dashboard de Render
