from rest_framework import serializers
from .models import Device, DeviceSale, DeviceInstallment
from core.utils import generate_payment_schedule
from datetime import date

    class Meta:
        model = Device
        fields = '__all__'



class DeviceInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceInstallment
        fields = '__all__'

class DeviceSaleSerializer(serializers.ModelSerializer):
    installments = DeviceInstallmentSerializer(many=True, read_only=True)
    device_details = DeviceSerializer(source='device', read_only=True)

    class Meta:
        model = DeviceSale
        fields = '__all__'
        read_only_fields = ('monto_total_deuda', 'monto_cuota')

    def create(self, validated_data):
        sale = DeviceSale.objects.create(**validated_data)
        
        if sale.tipo == 'Credito':
            # Generate Schedule
            schedule_dates = generate_payment_schedule(
                sale.fecha_venta, 
                sale.cuotas_totales, 
                sale.metodo_pago
            )
            
            cuotas = []
            for i, date_val in enumerate(schedule_dates):
                cuotas.append(DeviceInstallment(
                    sale=sale,
                    numero=i+1,
                    fecha_vencimiento=date_val,
                    monto=sale.monto_cuota
                ))
            
            DeviceInstallment.objects.bulk_create(cuotas)
            
        return sale
