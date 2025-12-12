from django.db import models
from users.models import Client
from datetime import date

class Device(models.Model):
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Vendido', 'Vendido'),
    ]

    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imei = models.CharField(max_length=20, unique=True)
    imei2 = models.CharField(max_length=20, blank=True, null=True)
    numero_serie = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    image = models.ImageField(upload_to='devices/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.imei}"

class DeviceSale(models.Model):
    TIPO_CHOICES = [
        ('Contado', 'Contado'),
        ('Credito', 'Credito'),
    ]
    METODO_PAGO_CHOICES = [
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Contado')
    fecha_venta = models.DateField(default=date.today)
    
    # Financials
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interes = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Percentage
    cuotas_totales = models.IntegerField(default=1)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, null=True, blank=True)
    
    # OS & iCloud
    sistema_operativo = models.CharField(max_length=20, choices=[('Android', 'Android'), ('IOS', 'IOS')], default='Android')
    icloud_email = models.EmailField(blank=True, null=True)
    icloud_password = models.CharField(max_length=100, blank=True, null=True)
    
    # Calculated
    monto_total_deuda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(max_length=20, default='Activo', choices=[('Activo', 'Activo'), ('Pagado', 'Pagado')])

    def save(self, *args, **kwargs):
        if self.tipo == 'Contado':
            self.monto_total_deuda = 0
            self.monto_cuota = 0
            self.estado = 'Pagado'
            self.cuotas_totales = 0
        elif not self.monto_total_deuda:
            restante = self.device.precio - self.monto_inicial
            if restante < 0: restante = 0
            
            self.monto_total_deuda = restante * (1 + (self.interes / 100))
            if self.cuotas_totales > 0:
                self.monto_cuota = self.monto_total_deuda / self.cuotas_totales
            else:
                self.monto_cuota = 0
        
        super().save(*args, **kwargs)
        
        # Mark device as sold
        self.device.estado = 'Vendido'
        self.device.save()

class DeviceInstallment(models.Model):
    sale = models.ForeignKey(DeviceSale, related_name='installments', on_delete=models.CASCADE)
    numero = models.IntegerField()
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=[('Yape', 'Yape'), ('Efectivo', 'Efectivo')], null=True, blank=True)

    def __str__(self):
        return f"Cuota {self.numero} - Device {self.sale.device.modelo}"
