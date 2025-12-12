from rest_framework import serializers
from .models import ContratoMoto, CuotaContrato
from core.utils import generate_payment_schedule
from datetime import date

class CuotaContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaContrato
        fields = '__all__'

class ContratoMotoSerializer(serializers.ModelSerializer):
    cuotas = CuotaContratoSerializer(many=True, read_only=True)

    class Meta:
        model = ContratoMoto
        fields = '__all__'
        read_only_fields = ('monto_total_deuda', 'monto_cuota')

    def create(self, validated_data):
        contrato = ContratoMoto.objects.create(**validated_data)
        
        # Generate Schedule
        schedule_dates = generate_payment_schedule(
            contrato.fecha_contrato, 
            contrato.cuotas_totales, 
            contrato.metodo_pago
        )
        
        cuotas = []
        for i, date_val in enumerate(schedule_dates):
            cuotas.append(CuotaContrato(
                contrato=contrato,
                numero=i+1,
                fecha_vencimiento=date_val,
                monto=contrato.monto_cuota
            ))
        
        CuotaContrato.objects.bulk_create(cuotas)
        return contrato
