# Sistema de Gestión de Préstamos

Un sistema web desarrollado en Django para la gestión de préstamos, clientes y pagos.

## Características

- Gestión de clientes
- Registro de préstamos
- Control de pagos y cuotas
- Calendario de pagos
- Reportes de pagos
- Interfaz web moderna

## Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Base de datos**: SQLite3
- **Frontend**: HTML, CSS, JavaScript (templates Django)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/prestamos.git
cd prestamos
```

2. Crea un entorno virtual:
```bash
python -m venv venv
```

3. Activa el entorno virtual:
```bash
# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Ejecuta las migraciones:
```bash
cd gestion_prestamos
python manage.py migrate
```

6. Crea un superusuario:
```bash
python manage.py createsuperuser
```

7. Ejecuta el servidor de desarrollo:
```bash
python manage.py runserver
```

8. Abre tu navegador y ve a `http://127.0.0.1:8000/`

## Estructura del Proyecto

```
prestamos/
├── gestion_prestamos/          # Configuración del proyecto Django
│   ├── gestion_prestamos/      # Configuración principal
│   ├── prestamos/              # Aplicación principal
│   │   ├── models.py           # Modelos de datos
│   │   ├── views.py            # Vistas
│   │   ├── forms.py            # Formularios
│   │   ├── templates/          # Plantillas HTML
│   │   └── migrations/         # Migraciones de base de datos
│   └── db.sqlite3             # Base de datos SQLite
├── venv/                      # Entorno virtual
├── requirements.txt           # Dependencias del proyecto
└── README.md                 # Este archivo
```

## Funcionalidades

### Gestión de Clientes
- Registro de nuevos clientes
- Edición de información de clientes
- Listado de clientes

### Gestión de Préstamos
- Creación de nuevos préstamos
- Asignación de préstamos a clientes
- Configuración de términos de pago

### Control de Pagos
- Registro de pagos realizados
- Seguimiento de cuotas pendientes
- Calendario de pagos

### Reportes
- Reportes de pagos por período
- Estado de préstamos
- Historial de transacciones

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Jhamir Quispe Santiago - jhamirquispe2007@gmail.com

Link del Proyecto: [https://github.com/jhamir14/prestamos](https://github.com/jhamir14/prestamos)

