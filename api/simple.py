def handler(request):
    """
    Simple handler that doesn't depend on Django database
    """
    try:
        path = request.get('path', '/')
        
        # Simple HTML response
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sistema de Gestión de Préstamos</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #007bff; color: white; padding: 20px; border-radius: 5px; }
                .content { padding: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Sistema de Gestión de Préstamos</h1>
                </div>
                <div class="content">
                    <h2>¡Aplicación funcionando correctamente!</h2>
                    <p>Tu aplicación Django está desplegada en Vercel.</p>
                    <p><strong>Ruta actual:</strong> {}</p>
                    <p><strong>Estado:</strong> ✅ Funcionando</p>
                    
                    <h3>Funcionalidades disponibles:</h3>
                    <ul>
                        <li>Gestión de clientes</li>
                        <li>Registro de préstamos</li>
                        <li>Control de pagos y cuotas</li>
                        <li>Calendario de pagos</li>
                        <li>Reportes de pagos</li>
                    </ul>
                    
                    <p><em>Nota: Para funcionalidad completa, se requiere configuración de base de datos.</em></p>
                </div>
            </div>
        </body>
        </html>
        """.format(path)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error: {str(e)}</h1>'
        }
