from django.core.management.base import BaseCommand
from prestamos.models import Prestamo


class Command(BaseCommand):
    help = "Regenera las cuotas de todos los préstamos preservando las cuotas pagadas, aplicando el nuevo reparto y redondeo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--solo-activos",
            action="store_true",
            help="Procesa solo préstamos activos (no cancelados)",
        )
        parser.add_argument(
            "--forma-pago",
            choices=["diario", "semanal"],
            help="Filtra por forma de pago",
        )

    def handle(self, *args, **options):
        solo_activos = options.get("solo_activos")
        forma_pago = options.get("forma_pago")

        qs = Prestamo.objects.all()
        if solo_activos:
            qs = qs.filter(estado=False)
        if forma_pago:
            qs = qs.filter(forma_pago=forma_pago)

        total = qs.count()
        procesados = 0
        self.stdout.write(self.style.NOTICE(f"Encontrados {total} préstamos para procesar."))

        for prestamo in qs.iterator():
            try:
                prestamo.regenerar_cuotas_preservando_pagadas()
                procesados += 1
            except Exception as e:
                self.stderr.write(f"Error en préstamo ID {prestamo.id}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Regeneración completada: {procesados}/{total} préstamos procesados."))