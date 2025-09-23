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
    def meses_totales(self):
        """Calcula el número de meses entre fecha de préstamo y vencimiento"""
        import calendar
        from datetime import datetime
        
        # Calcular la diferencia en meses
        fecha_inicio = self.fecha_prestamo
        fecha_fin = self.fecha_vencimiento
        
        # Diferencia en años y meses
        diff_years = fecha_fin.year - fecha_inicio.year
        diff_months = fecha_fin.month - fecha_inicio.month
        total_months = diff_years * 12 + diff_months
        
        # Si el día de vencimiento es mayor al día de inicio, cuenta como mes completo
        if fecha_fin.day > fecha_inicio.day:
            total_months += 1
        # Si es el mismo día o menor, pero hay diferencia de días significativa (>15), cuenta como mes adicional
        elif fecha_fin.day <= fecha_inicio.day:
            # Calcular días transcurridos en el mes actual
            try:
                fecha_inicio_mes_actual = fecha_inicio.replace(month=fecha_fin.month, year=fecha_fin.year)
                if fecha_inicio_mes_actual <= fecha_fin:
                    dias_en_mes_actual = (fecha_fin - fecha_inicio_mes_actual).days
                    if dias_en_mes_actual > 15:
                        total_months += 1
            except ValueError:
                # En caso de error (ej: 31 de enero vs 28 de febrero), usar cálculo simple
                total_months += 1
        
        return max(1, total_months)  # Mínimo 1 mes
    
    @property
    def porcentaje_interes_total(self):
        """Calcula el porcentaje total de interés basado en los meses"""
        meses = self.meses_totales
        # 20% por el primer mes + 20% por cada mes adicional
        return Decimal('0.20') * meses
    
    @property
    def monto_interes(self):
        """Calcula el monto del interés"""
        return self.monto * self.porcentaje_interes_total
    
    @property
    def monto_total(self):
        """Calcula el monto total con interés progresivo por meses"""
        return self.monto + self.monto_interes
    
    @property
    def dias_totales(self):
        """Calcula los días totales entre fecha de préstamo y vencimiento"""
        return (self.fecha_vencimiento - self.fecha_prestamo).days
    
    @property
    def numero_cuotas(self):
        """Calcula el número de cuotas basado en la modalidad de pago y días totales"""
        if self.forma_pago == 'diario':
            # Contar solo días laborables (lunes a sábado)
            from datetime import timedelta
            dias_laborables = 0
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado (0-5)
                    dias_laborables += 1
                current_date += timedelta(days=1)
            return dias_laborables
        else:  # semanal
            # Número de semanas completas
            return max(1, self.dias_totales // 7)
    
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
        
        if self.forma_pago == 'diario':
            # Cuotas diarias de lunes a sábado hasta la fecha de vencimiento
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado (0-5)
                    CuotaPago.objects.create(
                        prestamo=self,
                        fecha_pago=current_date,
                        monto=self.cuota_diaria,
                        tipo_cuota='diario'
                    )
                current_date += timedelta(days=1)
        else:  # semanal
            # Cuotas semanales hasta la fecha de vencimiento
            current_date = self.fecha_prestamo + timedelta(weeks=1)
            while current_date <= self.fecha_vencimiento:
                CuotaPago.objects.create(
                    prestamo=self,
                    fecha_pago=current_date,
                    monto=self.cuota_semanal,
                    tipo_cuota='semanal'
                )
                current_date += timedelta(weeks=1)
    
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