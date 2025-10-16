# Despliegue en Clouding (VPS)

Esta guía configura tu proyecto Django en un VPS de Clouding usando Gunicorn + Nginx y MySQL. Datos proporcionados:

- DNS: `65c69cf0-79ce-4b3f-bcec-f79d02f88417.clouding.host`
- IP pública: `79.143.91.254`

## Requisitos en el VPS

- Ubuntu/Debian actualizado con acceso SSH.
- Dominio apuntado (opcional, puedes usar el DNS de Clouding).
- MySQL local en el VPS o una base MySQL gestionada externa.

## 1) Preparar el servidor

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx git
```

## 2) Clonar el proyecto

```bash
sudo mkdir -p /srv/prestamos && sudo chown $USER:$USER /srv/prestamos
cd /srv/prestamos
git clone <URL_DE_TU_REPO> .
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Base de datos (MySQL)

Opción A: MySQL en el mismo VPS

```bash
sudo apt install -y mysql-server
sudo mysql -e "CREATE DATABASE IF NOT EXISTS prestamos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'prestamos_user'@'localhost' IDENTIFIED BY 'cambia-esta-clave';"
sudo mysql -e "GRANT ALL PRIVILEGES ON prestamos.* TO 'prestamos_user'@'localhost'; FLUSH PRIVILEGES;"
```

Define `DATABASE_URL`:

```bash
export DATABASE_URL="mysql://prestamos_user:cambia-esta-clave@127.0.0.1:3306/prestamos?charset=utf8mb4"
```

Opción B: MySQL gestionado externo (PlanetScale/Aiven/Railway)

- Usa el DSN que te entregue el proveedor, por ejemplo:
  `mysql://USER:PASS@HOST:3306/DBNAME?charset=utf8mb4`

## 4) Variables de entorno

```bash
export SECRET_KEY="cambia-esta-clave-segura"
export DEBUG="False"
export ALLOWED_HOSTS="65c69cf0-79ce-4b3f-bcec-f79d02f88417.clouding.host,79.143.91.254"
export CSRF_TRUSTED_ORIGINS="https://65c69cf0-79ce-4b3f-bcec-f79d02f88417.clouding.host"
```

Puedes guardar estas variables dentro del servicio systemd (más abajo) y omitir exportarlas manualmente.

## 5) Migraciones y estáticos

```bash
source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

## 6) Servicio systemd (Gunicorn)

Instala la unidad:

```bash
sudo cp deploy/clouding/prestamos.service /etc/systemd/system/prestamos.service
sudo sed -i "s|/srv/prestamos|/srv/prestamos|g" /etc/systemd/system/prestamos.service
sudo systemctl daemon-reload
sudo systemctl enable --now prestamos
```

Verifica:
```bash
sudo journalctl -u prestamos -f
```

## 7) Nginx reverse proxy

```bash
sudo cp deploy/clouding/prestamos.nginx.conf /etc/nginx/sites-available/prestamos
sudo ln -sf /etc/nginx/sites-available/prestamos /etc/nginx/sites-enabled/prestamos
sudo nginx -t && sudo systemctl reload nginx
```

El bloque usa `server_name` con el DNS proporcionado y sirve `/static/` desde `staticfiles`.

## 8) TLS (Let’s Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 65c69cf0-79ce-4b3f-bcec-f79d02f88417.clouding.host
```

## 9) Comprobación

- Abre `https://65c69cf0-79ce-4b3f-bcec-f79d02f88417.clouding.host/`
- Deberías ver la aplicación funcionando.

## 10) Importar datos desde tu MySQL local (opcional)

```bash
# En tu máquina local
mysqldump -h 127.0.0.1 -P 3307 -u root -p --default-character-set=utf8mb4 prestamos > dump.sql

# En el VPS
mysql -h 127.0.0.1 -P 3306 -u prestamos_user -p prestamos < dump.sql
```

## Notas

- El proyecto ya soporta MySQL via `dj-database-url` + `PyMySQL`.
- Ajusta `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` cuando uses dominio propio.
- Si tu proveedor MySQL exige SSL explícito, se puede ajustar `DATABASE_URL` o `OPTIONS` en `settings.py`.