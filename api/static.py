import os
from pathlib import Path

def handler(request):
    # Handle static files
    path = request.get('path', '')
    
    # Map static file requests
    if path.startswith('/static/'):
        static_path = Path(__file__).parent.parent / 'gestion_prestamos' / 'staticfiles' / path[8:]
        if static_path.exists():
            with open(static_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.png'):
                content_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': content_type,
                    'Cache-Control': 'public, max-age=31536000'
                },
                'body': content
            }
    
    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
