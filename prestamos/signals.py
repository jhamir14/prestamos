from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Prestamo


@receiver(pre_save, sender=Prestamo)
def marcar_regeneracion_si_cambios(sender, instance: Prestamo, **kwargs):
    """Marca que se necesita regenerar cuotas si cambian campos clave al editar."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    cambios = (
        old.monto != instance.monto or
        old.fecha_prestamo != instance.fecha_prestamo or
        old.fecha_vencimiento != instance.fecha_vencimiento or
        old.forma_pago != instance.forma_pago
    )
    if cambios:
        # Flag temporal usado en post_save
        instance._needs_regeneration = True

@receiver(post_save, sender=Prestamo)
def generar_cuotas_automaticamente(sender, instance: Prestamo, created: bool, **kwargs):
    """Genera cuotas automáticamente cuando se crea un préstamo."""
    if created:
        try:
            instance.generar_cuotas()
        except Exception:
            # Evitar romper el guardado del préstamo por errores de cuotas
            pass
    else:
        # Regenerar cuotas si hubo cambios en campos clave
        if getattr(instance, '_needs_regeneration', False):
            try:
                instance.regenerar_cuotas_preservando_pagadas()
            except Exception:
                # Evitar romper el guardado del préstamo por errores de cuotas
                pass