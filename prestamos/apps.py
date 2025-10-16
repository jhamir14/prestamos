from django.apps import AppConfig


class PrestamosConfig(AppConfig):
    name = 'prestamos'

    def ready(self):
        # Registrar señales
        from . import signals  # noqa: F401
