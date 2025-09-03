from django.forms import ModelForm
from django import forms
from datetime import date, timedelta
from .models import Prestamo, Cliente

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion', 'ciudad', 'pais']

class PrestamoForm(ModelForm):
    class Meta:
        model = Prestamo
        fields = ['cliente', 'monto', 'fecha_prestamo', 'fecha_vencimiento', 'forma_pago']
        widgets = {
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date', 'id': 'id_fecha_prestamo'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'id': 'id_fecha_vencimiento'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fechas automáticas solo para nuevos préstamos
        if not self.instance.pk:  # Solo para nuevos préstamos
            fecha_actual = date.today()
            fecha_vencimiento = fecha_actual + timedelta(days=30)  # Un mes después
            
            self.fields['fecha_prestamo'].initial = fecha_actual
            self.fields['fecha_vencimiento'].initial = fecha_vencimiento