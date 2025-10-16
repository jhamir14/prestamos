import os
from urllib.parse import urlparse

import pymysql


def ensure_mysql_database():
    url = os.environ.get('DATABASE_URL', 'mysql://root:261401@127.0.0.1:3307/prestamos')
    parsed = urlparse(url)

    db_name = (parsed.path or '/prestamos').lstrip('/')
    host = parsed.hostname or '127.0.0.1'
    port = parsed.port or 3306
    user = parsed.username or 'root'
    password = parsed.password or ''

    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
        print(f"✅ Base de datos asegurada: {db_name} en {host}:{port} como {user}")
    finally:
        conn.close()


if __name__ == '__main__':
    ensure_mysql_database()