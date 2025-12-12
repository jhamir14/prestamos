from django.db import models
from users.models import Client
from datetime import date

class Prestamo(models.Model):
    FRECUENCIA_CHOICES = [
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
    ]
    
    cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    monto_prestado = models.DecimalField(max_digits=10, decimal_places=2)
    interes = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    fecha_inicio = models.DateField(default=date.today)
    cuotas_totales = models.IntegerField()
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)
    estado = models.CharField(max_length=20, default='Activo', choices=[('Activo', 'Activo'), ('Pagado', 'Pagado')])
    monto_total_deuda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.monto_total_deuda:
            # Simple interest calculation based on the provided percentage
            self.monto_total_deuda = self.monto_prestado * (1 + (self.interes / 100))
            self.monto_cuota = self.monto_total_deuda / self.cuotas_totales
        super().save(*args, **kwargs)

class CuotaPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, related_name='cuotas', on_delete=models.CASCADE)
    numero = models.IntegerField()
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=[('Yape', 'Yape'), ('Efectivo', 'Efectivo')], null=True, blank=True)

    def __str__(self):
        return f"Cuota {self.numero} - Préstamo {self.prestamo.id}"
