from gestion_prestamos.wsgi import application

def handler(request):
    return application(request)
