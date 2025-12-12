from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_gmail(value):
    if not value.endswith('@gmail.com'):
        raise ValidationError("El correo debe ser @gmail.com")

class Client(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(validators=[validate_gmail])
    domicilio = models.TextField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
