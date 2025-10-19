from django.db import models
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
    forma_pago = models.CharField(max_length=10, choices=FORMA_PAGO_CHOICES, default='diario', db_index=True)
    estado = models.BooleanField(default=False, db_index=True)
    
    # Eliminado meses_totales (no usado) para simplificar lógica
    
    @property
    def porcentaje_interes_total(self):
        """Calcula el porcentaje total de interés basado en quincenas (15 días)"""
        quincenas = self.quincenas_totales
        # 10% por cada quincena (15 días)
        return Decimal('0.10') * quincenas
    
    @property
    def monto_interes(self):
        """Calcula el monto del interés"""
        return self.monto * self.porcentaje_interes_total
    
    @property
    def monto_total(self):
        """Calcula el monto total con interés progresivo por quincenas"""
        return self.monto + self.monto_interes
    
    @property
    def dias_totales(self):
        """Calcula los días totales entre fecha de préstamo y vencimiento"""
        return (self.fecha_vencimiento - self.fecha_prestamo).days

    @property
    def quincenas_totales(self):
        """Calcula el número de quincenas (periodos de 15 días) entre préstamo y vencimiento"""
        from math import ceil
        dias = max(0, self.dias_totales)
        return max(1, ceil(dias / 15))
    
    @property
    def numero_cuotas(self):
        """Calcula el número de cuotas basado en la modalidad de pago y días totales"""
        from datetime import timedelta
        if self.forma_pago == 'diario':
            # Calcular días laborables (lunes a sábado) sin bucles
            if self.fecha_vencimiento <= self.fecha_prestamo:
                return 0
            total_days = (self.fecha_vencimiento - self.fecha_prestamo).days
            start = self.fecha_prestamo + timedelta(days=1)
            end = self.fecha_vencimiento
            start_weekday = start.weekday()  # 0=lunes, ..., 6=domingo
            first_sunday_delta = (6 - start_weekday) % 7
            first_sunday = start + timedelta(days=first_sunday_delta)
            if first_sunday > end:
                sundays = 0
            else:
                sundays = ((end - first_sunday).days // 7) + 1
            dias_laborables = total_days - sundays
            return max(0, dias_laborables)
        else:  # semanal
            # Redondeo hacia arriba de semanas
            dias = max(0, self.dias_totales)
            return max(1, (dias + 6) // 7)
    
    @property
    def monto_por_cuota(self):
        """Calcula el monto por cuota dividiendo el monto total entre el número de cuotas"""
        num_cuotas = self.numero_cuotas
        if num_cuotas > 0:
            return self.monto_total / Decimal(str(num_cuotas))
        return self.monto_total
    
    @property
    def cuota_diaria(self):
        """Calcula la cuota diaria basada en los días laborables hasta el vencimiento"""
        return self.monto_por_cuota
    
    @property
    def cuota_semanal(self):
        """Calcula la cuota semanal basada en las semanas hasta el vencimiento"""
        return self.monto_por_cuota
    
    def generar_cuotas(self):
        """Genera automáticamente todas las cuotas del préstamo basado en la fecha de vencimiento"""
        from datetime import timedelta
        
        # Limpiar cuotas existentes
        self.cuotas.all().delete()
        
        bulk = []
        if self.forma_pago == 'diario':
            # Cuotas diarias de lunes a sábado hasta la fecha de vencimiento
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado (0-5)
                    bulk.append(CuotaPago(
                        prestamo=self,
                        fecha_pago=current_date,
                        monto=self.cuota_diaria,
                        tipo_cuota='diario'
                    ))
                current_date += timedelta(days=1)
        else:  # semanal
            # Cuotas semanales hasta la fecha de vencimiento
            current_date = self.fecha_prestamo + timedelta(weeks=1)
            while current_date <= self.fecha_vencimiento:
                bulk.append(CuotaPago(
                    prestamo=self,
                    fecha_pago=current_date,
                    monto=self.cuota_semanal,
                    tipo_cuota='semanal'
                ))
                current_date += timedelta(weeks=1)
        
        if bulk:
            CuotaPago.objects.bulk_create(bulk)
    
    def __str__(self):
        return f"{self.cliente.nombre} - ${self.monto}"

class CuotaPago(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='cuotas')
    fecha_pago = models.DateField(db_index=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False, db_index=True)
    fecha_pagada = models.DateField(null=True, blank=True)
    tipo_cuota = models.CharField(max_length=10, choices=[('diario', 'Diario'), ('semanal', 'Semanal')])
    
    class Meta:
        unique_together = ['prestamo', 'fecha_pago']
        indexes = [
            models.Index(fields=['prestamo', 'fecha_pago']),
            models.Index(fields=['prestamo', 'pagada']),
            models.Index(fields=['fecha_pago', 'pagada']),
        ]
    
    def __str__(self):
        return f"{self.prestamo.cliente.nombre} - {self.fecha_pago} - ${self.monto}"