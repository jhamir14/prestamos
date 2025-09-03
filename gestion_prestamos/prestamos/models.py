from django.db import models
from django.utils import timezone
from decimal import Decimal

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Prestamo(models.Model):
    FORMA_PAGO_CHOICES = [
        ('diario', 'Diario (Lunes a Sábado)'),
        ('semanal', 'Semanal'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_prestamo = models.DateField()
    fecha_vencimiento = models.DateField()
    forma_pago = models.CharField(max_length=10, choices=FORMA_PAGO_CHOICES, default='diario')
    estado = models.BooleanField(default=False)
    
    @property
    def monto_total(self):
        """Calcula el monto total con 20% de interés"""
        return self.monto * Decimal('1.20')
    
    @property
    def cuota_diaria(self):
        """Calcula la cuota diaria (monto total / 24)"""
        return self.monto_total / Decimal('24')
    
    @property
    def cuota_semanal(self):
        """Calcula la cuota semanal (monto total / 4)"""
        return self.monto_total / Decimal('4')
    
    def generar_cuotas(self):
        """Genera automáticamente todas las cuotas del préstamo"""
        from datetime import timedelta
        
        # Limpiar cuotas existentes
        self.cuotas.all().delete()
        
        if self.forma_pago == 'diario':
            # Cuotas diarias de lunes a sábado - la primera cuota es un día después del préstamo
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado
                    CuotaPago.objects.create(
                        prestamo=self,
                        fecha_pago=current_date,
                        monto=self.cuota_diaria,
                        tipo_cuota='diario'
                    )
                current_date += timedelta(days=1)
        else:
            # Cuotas semanales - la primera cuota es una semana después del préstamo
            current_date = self.fecha_prestamo + timedelta(weeks=1)
            week_count = 0
            while current_date <= self.fecha_vencimiento and week_count < 4:
                CuotaPago.objects.create(
                    prestamo=self,
                    fecha_pago=current_date,
                    monto=self.cuota_semanal,
                    tipo_cuota='semanal'
                )
                current_date += timedelta(weeks=1)
                week_count += 1
    
    def __str__(self):
        return f"{self.cliente.nombre} - ${self.monto}"

class CuotaPago(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='cuotas')
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)
    fecha_pagada = models.DateField(null=True, blank=True)
    tipo_cuota = models.CharField(max_length=10, choices=[('diario', 'Diario'), ('semanal', 'Semanal')])
    
    class Meta:
        unique_together = ['prestamo', 'fecha_pago']
    
    def __str__(self):
        return f"{self.prestamo.cliente.nombre} - {self.fecha_pago} - ${self.monto}"