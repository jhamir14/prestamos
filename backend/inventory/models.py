from django.db import models

class Moto(models.Model):
    CONDICION_CHOICES = [
        ('0km', '0km'),
        ('Segunda', 'Segunda'),
    ]
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Alquilada', 'Alquilada'),
        ('Vendida', 'Vendida'),
    ]

    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    numero_motor = models.CharField(max_length=50)
    numero_serie = models.CharField(max_length=50)
    anio = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')
    image = models.ImageField(upload_to='motos/', null=True, blank=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"
