from django.db import models
from users.models import Client
from inventory.models import Moto
from decimal import Decimal
from datetime import date

class ContratoMoto(models.Model):
    METODO_PAGO_CHOICES = [
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
    ]
    TIPO_CHOICES = [
        ('Venta', 'Venta'),
        ('Alquiler', 'Alquiler'),
    ]

    cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Venta')
    fecha_contrato = models.DateField(default=date.today)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    interes = models.DecimalField(max_digits=5, decimal_places=2, default=54.47)
    cuotas_totales = models.IntegerField()
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(max_length=20, default='Activo', choices=[('Activo', 'Activo'), ('Pagado', 'Pagado')])
    monto_total_deuda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.monto_total_deuda:
            restante = self.moto.precio - self.monto_inicial
            # Interest is percentage, e.g. 54.47
            self.monto_total_deuda = restante * (1 + (self.interes / 100))
            self.monto_cuota = self.monto_total_deuda / self.cuotas_totales
        
        super().save(*args, **kwargs)
        
        # Update Moto status
        if self.tipo == 'Venta':
            self.moto.estado = 'Vendida'
        else:
            self.moto.estado = 'Alquilada'
        self.moto.save()

class CuotaContrato(models.Model):
    contrato = models.ForeignKey(ContratoMoto, related_name='cuotas', on_delete=models.CASCADE)
    numero = models.IntegerField()
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=[('Yape', 'Yape'), ('Efectivo', 'Efectivo')], null=True, blank=True)

    def __str__(self):
        return f"Cuota {self.numero} - {self.contrato}"
