import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"Error en {request.path}: {exception}")
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Ha ocurrido un error interno del servidor',
                'status': 500
            }, status=500)
        
        # Para peticiones normales, mostrar página de error personalizada
        return render(request, 'error_500.html', {
            'error': str(exception),
            'path': request.path
        }, status=500)
