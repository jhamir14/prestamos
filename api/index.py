import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_prestamos.settings')

import django
from django.core.wsgi import get_wsgi_application

# Initialize Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

def handler(request):
    try:
        # Handle the request using Django's WSGI application
        return application(request)
    except Exception as e:
        print(f"Error in handler: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': f'Internal Server Error: {str(e)}'
        }
