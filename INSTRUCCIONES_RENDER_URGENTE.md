# 🚨 Solución Urgente para Error en Render

## ❓ ¿Qué Error Estás Viendo?

**Por favor, comparte el error específico que aparece en Render para darte una solución exacta.**

Mientras tanto, aquí están las soluciones para los errores más comunes:

## 🔧 Solución Rápida (5 minutos)

### **Paso 1: Configurar Build Command**

En Render, ve a tu servicio → Build & Deploy → Build Command y cambia a:

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### **Paso 2: Verificar Variables de Entorno**

En Render, ve a tu servicio → Environment y asegúrate de tener:

```
DATABASE_URL=postgresql://userprestamos:ATyW0J5mWTpuOlSDubTarrsSeOQY9WkC@dpg-d2ufm7be5dus73en418g-a.oregon-postgres.render.com:5432/dbprestamos
SECRET_KEY=tu-clave-secreta-generada-por-render
DEBUG=False
ALLOWED_HOSTS=prestamos-jrnd.onrender.com
CSRF_TRUSTED_ORIGINS=https://prestamos-jrnd.onrender.com
```

### **Paso 3: Hacer Deploy Manual**

1. Haz clic en "Manual Deploy"
2. Selecciona "Deploy latest commit"
3. Espera a que termine el build

## 🚨 Errores Comunes y Soluciones

### **Error 1: Build Failed**
```
E: List directory /var/lib/apt/lists/partial is missing
```
**✅ Solución:** Usar el Build Command de arriba

### **Error 2: Database Connection**
```
django.db.utils.OperationalError: could not connect to server
```
**✅ Solución:** Verificar que DATABASE_URL esté configurada correctamente

### **Error 3: Static Files**
```
django.core.exceptions.ImproperlyConfigured
```
**✅ Solución:** El Build Command ya incluye collectstatic

### **Error 4: Module Not Found**
```
ModuleNotFoundError: No module named 'psycopg2'
```
**✅ Solución:** Ya está solucionado en requirements.txt

## 🔍 Diagnóstico Rápido

### **Verificar Logs en Render:**
1. Ve a tu servicio en Render
2. Haz clic en "Logs"
3. Busca el error específico
4. Comparte el error conmigo

### **Verificar Localmente:**
```bash
# Ejecutar este comando localmente
python verificar_render.py
```

## 🚀 Configuración Final

### **Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### **Start Command:**
```bash
gunicorn gestion_prestamos.wsgi:application
```

### **Health Check Path:**
```
/
```

## 📋 Checklist de Verificación

- [ ] Build Command configurado correctamente
- [ ] Variables de entorno configuradas
- [ ] Deploy manual ejecutado
- [ ] Logs revisados
- [ ] Aplicación accesible

## 🆘 Si Aún No Funciona

**Por favor, comparte:**
1. El error específico que aparece en los logs de Render
2. Una captura de pantalla del error
3. Las variables de entorno que tienes configuradas

## 📞 Próximos Pasos

1. **Aplica la solución rápida de arriba**
2. **Haz un deploy manual**
3. **Revisa los logs**
4. **Compárteme el error específico si persiste**

## ✅ Archivos Actualizados

He actualizado estos archivos para solucionar los problemas comunes:
- ✅ `requirements.txt` - psycopg2-binary para compatibilidad
- ✅ `build_render_final.sh` - Script de build mejorado
- ✅ `gestion_prestamos/settings.py` - Manejo de errores mejorado
- ✅ `verificar_render.py` - Script de diagnóstico

## 🎯 Resultado Esperado

Después de aplicar estas soluciones:
- ✅ Build exitoso sin errores
- ✅ Aplicación accesible en https://prestamos-jrnd.onrender.com
- ✅ Base de datos conectada
- ✅ Autocompletado funcionando
- ✅ Zona horaria peruana configurada
