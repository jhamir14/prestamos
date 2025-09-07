# Guía de Despliegue en Render - Solución de Error psycopg2

## ❌ Error Actual
```
django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module
```

## ✅ Solución Implementada

### 1. Archivos Actualizados

#### `requirements.txt` - Dependencias optimizadas
```
Django==5.2.5
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
psycopg2==2.9.9
djangorestframework==3.16.1
reportlab==4.0.8
Pillow==10.4.0
```

#### `runtime.txt` - Versión de Python
```
python-3.11.10
```

#### `build_simple.sh` - Script de build simplificado
```bash
#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### 2. Configuración en Render

#### Variables de Entorno Requeridas:
```
DATABASE_URL=postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos
SECRET_KEY=tu-clave-secreta-generada-por-render
DEBUG=False
ALLOWED_HOSTS=prestamos-jrnd.onrender.com
CSRF_TRUSTED_ORIGINS=https://prestamos-jrnd.onrender.com
```

#### Configuración de Build:
- **Build Command**: `./build_simple.sh`
- **Start Command**: `gunicorn gestion_prestamos.wsgi:application`
- **Health Check Path**: `/`

### 3. Pasos para Desplegar

1. **Sube los cambios** a GitHub
2. **En Render, actualiza la configuración**:
   - Cambia el Build Command a `./build_simple.sh`
   - Verifica que todas las variables de entorno estén configuradas
3. **Haz un Manual Deploy**

### 4. Si el Error Persiste

#### Opción A: Usar psycopg2-binary
Cambia en `requirements.txt`:
```
psycopg2-binary==2.9.9
```

#### Opción B: Usar psycopg3
Cambia en `requirements.txt`:
```
psycopg[binary]==3.1.18
```

#### Opción C: Build Command Personalizado
En Render, usa este Build Command:
```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### 5. Verificación

Después del despliegue exitoso:
- ✅ La aplicación carga en `https://prestamos-jrnd.onrender.com`
- ✅ No hay errores de psycopg2 en los logs
- ✅ La base de datos PostgreSQL está conectada
- ✅ Las migraciones se ejecutaron correctamente

## 🔧 Troubleshooting

### Si ves errores de permisos:
- Verifica que `build_simple.sh` tenga permisos de ejecución
- En Render, el Build Command debe ser `chmod +x build_simple.sh && ./build_simple.sh`

### Si hay problemas con la versión de Python:
- Render debería usar automáticamente la versión especificada en `runtime.txt`
- Si no, especifica manualmente Python 3.11 en la configuración de Render

### Si la base de datos no se conecta:
- Verifica que la URL de la base de datos sea correcta
- Asegúrate de que la base de datos esté en la misma región (Oregon)
- Verifica que las credenciales sean correctas
