from django.db import models
from decimal import Decimal, ROUND_HALF_UP

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
        """Calcula el número de cuotas utilizando el calendario programado real."""
        return len(self._fechas_programadas())
    
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
        
        # Construir fechas programadas reales según modalidad
        fechas = []
        if self.forma_pago == 'diario':
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado (0-5)
                    fechas.append(current_date)
                current_date += timedelta(days=1)
            # Asegurar que la última cuota coincida exactamente con la fecha de vencimiento
            if not fechas or fechas[-1] < self.fecha_vencimiento:
                fechas.append(self.fecha_vencimiento)
        else:  # semanal
            current_date = self.fecha_prestamo + timedelta(weeks=1)
            while current_date <= self.fecha_vencimiento:
                fechas.append(current_date)
                current_date += timedelta(weeks=1)
            # Si no hay fechas o la última es menor al vencimiento, asegurar que la última cuota sea en la fecha de vencimiento
            if not fechas or fechas[-1] < self.fecha_vencimiento:
                fechas.append(self.fecha_vencimiento)

        num_cuotas_real = len(fechas)
        if num_cuotas_real == 0:
            return
        monto_total = self.monto_total
        base = (monto_total / Decimal(str(num_cuotas_real))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Generar cuotas con ajuste de última cuota para sumar exactamente el total
        bulk = []
        for idx, fecha in enumerate(fechas):
            if idx < num_cuotas_real - 1:
                monto = base
            else:
                monto = (monto_total - (base * Decimal(str(num_cuotas_real - 1)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            bulk.append(CuotaPago(
                prestamo=self,
                fecha_pago=fecha,
                monto=monto,
                tipo_cuota=('diario' if self.forma_pago == 'diario' else 'semanal')
            ))

        if bulk:
            CuotaPago.objects.bulk_create(bulk)

    def _fechas_programadas(self):
        """Retorna la lista de fechas programadas según forma de pago y rango de fechas.

        Para semanal, se generan incrementos de 7 días desde la fecha de préstamo y se
        asegura que la última fecha sea la `fecha_vencimiento`.
        Para diario, se listan lunes a sábado sin recortes y se asegura
        que la última fecha coincida con `fecha_vencimiento`.
        """
        from datetime import timedelta
        fechas = []
        if self.forma_pago == 'diario':
            current_date = self.fecha_prestamo + timedelta(days=1)
            while current_date <= self.fecha_vencimiento:
                if current_date.weekday() < 6:  # Lunes a sábado
                    fechas.append(current_date)
                current_date += timedelta(days=1)
            if not fechas or fechas[-1] < self.fecha_vencimiento:
                fechas.append(self.fecha_vencimiento)
        else:
            current_date = self.fecha_prestamo + timedelta(weeks=1)
            while current_date <= self.fecha_vencimiento:
                fechas.append(current_date)
                current_date += timedelta(weeks=1)
            if not fechas or fechas[-1] < self.fecha_vencimiento:
                fechas.append(self.fecha_vencimiento)
        return fechas

    def regenerar_cuotas_preservando_pagadas(self):
        """Regenera cuotas tras editar el préstamo, preservando cuotas ya pagadas.

        - Elimina solo cuotas no pagadas.
        - Genera nuevas cuotas para el nuevo calendario.
        - Ajusta el monto de las nuevas cuotas para cubrir el saldo restante.
        """
        # Preservar cuotas pagadas existentes
        cuotas_pagadas = list(self.cuotas.filter(pagada=True))

        # Eliminar solo cuotas no pagadas
        self.cuotas.filter(pagada=False).delete()

        # Calcular nuevo calendario de fechas (robusto)
        fechas_nuevas = self._fechas_programadas()

        # Fechas ya pagadas para evitar duplicados
        fechas_pagadas = {c.fecha_pago for c in cuotas_pagadas}

        # Calcular saldo restante y número de cuotas pendientes
        monto_pagado = sum((c.monto for c in cuotas_pagadas), Decimal('0'))
        saldo_restante = self.monto_total - monto_pagado

        # Cuotas pendientes a generar según nuevo calendario
        fechas_pendientes = [f for f in fechas_nuevas if f not in fechas_pagadas]
        pendientes_count = len(fechas_pendientes)

        # Crear cuotas nuevas para fechas pendientes con redondeo y ajuste final
        nuevas = []
        tipo = 'diario' if self.forma_pago == 'diario' else 'semanal'
        if pendientes_count > 0:
            base = (saldo_restante / Decimal(str(pendientes_count))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for idx, fecha in enumerate(fechas_pendientes):
                if idx < pendientes_count - 1:
                    monto_i = base
                else:
                    monto_i = (saldo_restante - (base * Decimal(str(pendientes_count - 1)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                nuevas.append(CuotaPago(
                    prestamo=self,
                    fecha_pago=fecha,
                    monto=monto_i,
                    tipo_cuota=tipo
                ))

        if nuevas:
            CuotaPago.objects.bulk_create(nuevas)
    
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