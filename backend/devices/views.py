from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date
from .models import Device, DeviceSale, DeviceInstallment
from .serializers import DeviceSerializer, DeviceSaleSerializer, DeviceInstallmentSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceSaleViewSet(viewsets.ModelViewSet):
    queryset = DeviceSale.objects.all()
    serializer_class = DeviceSaleSerializer

class DeviceInstallmentViewSet(viewsets.ModelViewSet):
    queryset = DeviceInstallment.objects.all()
    serializer_class = DeviceInstallmentSerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        cuota = self.get_object()
        monto_pago = float(request.data.get('monto', 0))
        metodo = request.data.get('metodo_pago', 'Efectivo')

        if monto_pago <= 0:
            return Response({'error': 'Monto inválido'}, status=400)

        cuota.monto_pagado = float(cuota.monto_pagado) + monto_pago
        cuota.metodo_pago = metodo
        
        if cuota.monto_pagado >= float(cuota.monto):
            cuota.pagado = True
            cuota.fecha_pago = date.today()
        
        cuota.save()
        
        # Update Sale Status
        sale = cuota.sale
        if not sale.installments.filter(pagado=False).exists():
            sale.estado = 'Pagado'
        else:
            sale.estado = 'Activo'
        sale.save()

        return Response(DeviceInstallmentSerializer(cuota).data)
