import os
from urllib.parse import urlparse

import pymysql


def main():
    db_url = os.environ.get(
        "DATABASE_URL",
        "mysql://root:261401@127.0.0.1:3307/prestamos",
    )
    parsed = urlparse(db_url)

    host = parsed.hostname or "127.0.0.1"
    port = int(parsed.port or 3306)
    user = parsed.username or "root"
    password = parsed.password or ""
    db_name = (parsed.path or "/").lstrip("/") or "prestamos"

    app_user = os.environ.get("APP_DB_USER", "prestamos_app")
    app_pass = os.environ.get("APP_DB_PASSWORD", "PrestamosApp_261401")
    app_host = os.environ.get("APP_DB_HOST", "127.0.0.1")

    conn = pymysql.connect(host=host, port=port, user=user, password=password, autocommit=True)
    with conn.cursor() as cur:
        try:
            # Crear usuario si no existe
            cur.execute(f"CREATE USER IF NOT EXISTS '{app_user}'@'{app_host}' IDENTIFIED BY %s", (app_pass,))
            # Otorgar privilegios sobre la base de datos especificada
            cur.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{app_user}'@'{app_host}'")
            cur.execute("FLUSH PRIVILEGES")
        except pymysql.err.OperationalError as e:
            if e.args and e.args[0] == 1030:
                # Error 176 Aria: intentar reparar tablas del esquema mysql y reintentar
                print("⚠️ Detectado error Aria (1030). Intentando REPAIR TABLE en mysql.user y mysql.db...")
                try:
                    cur.execute("CHECK TABLE mysql.user")
                except Exception:
                    pass
                try:
                    cur.execute("REPAIR TABLE mysql.user")
                except Exception:
                    pass
                try:
                    cur.execute("CHECK TABLE mysql.db")
                except Exception:
                    pass
                try:
                    cur.execute("REPAIR TABLE mysql.db")
                except Exception:
                    pass
                # Reintento
                cur.execute(f"CREATE USER IF NOT EXISTS '{app_user}'@'{app_host}' IDENTIFIED BY %s", (app_pass,))
                cur.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{app_user}'@'{app_host}'")
                cur.execute("FLUSH PRIVILEGES")
            else:
                raise
    conn.close()
    print(f"✅ Usuario '{app_user}'@'{app_host}' creado y con permisos sobre {db_name}.*")


if __name__ == "__main__":
    main()