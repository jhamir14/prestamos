# 👑 Crear Superusuario en Render

## 🚀 Métodos para Crear Superusuario

### **Método 1: Automático en Build (Recomendado)**

Tu aplicación ya está configurada para crear automáticamente el superusuario durante el despliegue. Las credenciales son:

- **Usuario**: `jhamir14`
- **Contraseña**: `jhamirquispe`
- **Email**: `admin@example.com`

### **Método 2: Shell de Render**

1. **Ve a tu servicio en Render**
2. **Haz clic en "Shell"** (menú lateral)
3. **Ejecuta:**
```bash
python manage.py createsuperuser
```
4. **Sigue las instrucciones** para crear el usuario

### **Método 3: Script Personalizado**

1. **En el Shell de Render, ejecuta:**
```bash
python create_superuser.py
```

### **Método 4: Comando Directo**

En el Shell de Render:
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('jhamir14', 'admin@example.com', 'jhamirquispe')
print('Superusuario creado!')
"
```

## 📋 Credenciales del Superusuario

- **Usuario**: `jhamir14`
- **Contraseña**: `jhamirquispe`
- **Email**: `admin@example.com`
- **URL del Admin**: `https://prestamos-jrnd.onrender.com/admin/`

## 🔧 Verificar que Funciona

1. **Ve a**: `https://prestamos-jrnd.onrender.com/admin/`
2. **Inicia sesión** con las credenciales de arriba
3. **Deberías ver** el panel de administración de Django

## 🛠️ Cambiar Contraseña

Si quieres cambiar la contraseña del superusuario:

```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='jhamir14')
user.set_password('nueva_contraseña')
user.save()
print('Contraseña actualizada!')
"
```

## 🔍 Listar Usuarios

Para ver todos los usuarios en la base de datos:

```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.all():
    print(f'Usuario: {user.username}, Email: {user.email}, Superusuario: {user.is_superuser}')
"
```

## ✅ Verificación Final

Después de crear el superusuario:

1. ✅ Puedes acceder al admin de Django
2. ✅ Puedes crear, editar y eliminar clientes
3. ✅ Puedes gestionar préstamos y cuotas
4. ✅ Tienes acceso completo a todas las funcionalidades

¡Tu sistema de gestión de préstamos está listo para usar! 🎉
