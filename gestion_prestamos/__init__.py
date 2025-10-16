try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # Si PyMySQL no está instalado aún, la importación fallará.
    # La aplicación seguirá cargando, pero el motor MySQL requerirá
    # que PyMySQL esté presente para funcionar.
    pass