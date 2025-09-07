# Variables de Entorno para Render

## Configuración de tu Base de Datos PostgreSQL

Tu base de datos PostgreSQL ya está configurada con estos datos:

### Información de Conexión
- **Hostname**: `dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com`
- **Puerto**: `5432`
- **Base de datos**: `dbprestamos`
- **Usuario**: `userprestamos`
- **Contraseña**: `ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC`

### URL de Conexión
```
postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos
```

## Variables de Entorno para tu Servicio Web

Cuando configures tu servicio web en Render, agrega estas variables de entorno:

### Variables Requeridas
```
SECRET_KEY=tu-clave-secreta-generada-por-render
DEBUG=False
ALLOWED_HOSTS=gestion-prestamos.onrender.com
DATABASE_URL=postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos
CSRF_TRUSTED_ORIGINS=https://gestion-prestamos.onrender.com
```

### Cómo Configurar en Render

1. **Ve a tu servicio web** en el dashboard de Render
2. **Selecciona "Environment"** en el menú lateral
3. **Agrega cada variable** una por una:

#### Variable 1: SECRET_KEY
- **Key**: `SECRET_KEY`
- **Value**: `tu-clave-secreta-generada-por-render` (Render la genera automáticamente)

#### Variable 2: DEBUG
- **Key**: `DEBUG`
- **Value**: `False`

#### Variable 3: ALLOWED_HOSTS
- **Key**: `ALLOWED_HOSTS`
- **Value**: `gestion-prestamos.onrender.com`

#### Variable 4: DATABASE_URL
- **Key**: `DATABASE_URL`
- **Value**: `postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos`

#### Variable 5: CSRF_TRUSTED_ORIGINS
- **Key**: `CSRF_TRUSTED_ORIGINS`
- **Value**: `https://gestion-prestamos.onrender.com`

## Pasos para Desplegar

1. **Sube tu código** a GitHub (si no lo has hecho)
2. **Conecta tu repositorio** a Render
3. **Configura las variables de entorno** (arriba)
4. **Despliega el servicio**
5. **Ejecuta las migraciones** (se harán automáticamente)

## Verificación

Después del despliegue, verifica que:
- ✅ La aplicación carga correctamente
- ✅ Puedes acceder al admin de Django
- ✅ Los modelos funcionan (clientes, préstamos, cuotas)
- ✅ No hay errores en los logs

## Migración de Datos (Si tienes datos en SQLite)

Si tienes datos existentes en SQLite que quieres transferir:

1. **Ejecuta localmente**:
   ```bash
   python migrate_sqlite_to_postgres.py export
   ```

2. **Sube los archivos JSON** a tu servidor

3. **Ejecuta en el servidor**:
   ```bash
   python migrate_sqlite_to_postgres.py import
   ```

¡Tu aplicación estará lista para usar PostgreSQL! 🚀
