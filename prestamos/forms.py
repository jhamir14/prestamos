from django.forms import ModelForm
from django import forms
from datetime import date, timedelta
from .models import Prestamo, Cliente

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion', 'ciudad', 'pais']

class PrestamoForm(ModelForm):
    # Campo personalizado para el autocompletado de clientes
    cliente_busqueda = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar cliente por nombre, email o teléfono...',
            'id': 'cliente-busqueda',
            'autocomplete': 'off'
        }),
        label='Buscar Cliente'
    )
    
    class Meta:
        model = Prestamo
        fields = ['cliente', 'monto', 'fecha_prestamo', 'fecha_vencimiento', 'forma_pago']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control', 'id': 'id_cliente', 'style': 'display: none;'}),
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date', 'id': 'id_fecha_prestamo', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'id': 'id_fecha_vencimiento', 'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fechas automáticas solo para nuevos préstamos
        if not self.instance.pk:  # Solo para nuevos préstamos
            fecha_actual = date.today()
            fecha_vencimiento = fecha_actual + timedelta(days=30)  # Un mes después
            
            self.fields['fecha_prestamo'].initial = fecha_actual
            self.fields['fecha_vencimiento'].initial = fecha_vencimiento
        
        # Agregar ayuda para los campos
        self.fields['fecha_vencimiento'].help_text = "El número de cuotas se calculará automáticamente según esta fecha y la modalidad de pago. El interés es quincenal y progresivo: 10% por cada 15 días; desde 16 días ya es 20%, y así sucesivamente."
        self.fields['forma_pago'].help_text = "Diario: Se calculan cuotas de lunes a sábado. Semanal: Se calculan cuotas cada 7 días."
        self.fields['monto'].help_text = "Monto base del préstamo. El interés se aplica progresivamente por quincenas: 10% por la primera quincena, 20% por dos quincenas, 30% por tres quincenas, etc."
        
        # Si hay un cliente seleccionado, mostrar su información en el campo de búsqueda
        if self.instance.pk and self.instance.cliente:
            self.fields['cliente_busqueda'].initial = f"{self.instance.cliente.nombre} - {self.instance.cliente.email} - {self.instance.cliente.telefono}"