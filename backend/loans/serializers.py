from rest_framework import serializers
from .models import Prestamo, CuotaPrestamo
from core.utils import generate_payment_schedule

class CuotaPrestamoSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = CuotaPrestamo
        fields = '__all__'

    def get_client_name(self, obj):
        return f"{obj.prestamo.cliente.nombres} {obj.prestamo.cliente.apellidos}"

class PrestamoSerializer(serializers.ModelSerializer):
    cuotas = CuotaPrestamoSerializer(many=True, read_only=True)

    class Meta:
        model = Prestamo
        fields = '__all__'
        read_only_fields = ('monto_total_deuda', 'monto_cuota')

    def create(self, validated_data):
        prestamo = Prestamo.objects.create(**validated_data)
        
        # Generate Schedule
        schedule_dates = generate_payment_schedule(
            prestamo.fecha_inicio, 
            prestamo.cuotas_totales, 
            prestamo.frecuencia
        )
        
        cuotas = []
        for i, date_val in enumerate(schedule_dates):
            cuotas.append(CuotaPrestamo(
                prestamo=prestamo,
                numero=i+1,
                fecha_vencimiento=date_val,
                monto=prestamo.monto_cuota
            ))
        
        CuotaPrestamo.objects.bulk_create(cuotas)
        return prestamo
