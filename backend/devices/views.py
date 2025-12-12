from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date
from .models import Device, DeviceSale, DeviceInstallment
from .serializers import DeviceSerializer, DeviceSaleSerializer, DeviceInstallmentSerializer
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceSaleViewSet(viewsets.ModelViewSet):
    queryset = DeviceSale.objects.all()
    serializer_class = DeviceSaleSerializer

    @action(detail=True, methods=['get'])
    def download_schedule_pdf(self, request, pk=None):
        sale = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"{sale.cliente.nombres}_{sale.cliente.apellidos}_venta_celular.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Calendario de Pagos - Venta Celular #{sale.id}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Details
        elements.append(Paragraph(f"<b>Cliente:</b> {sale.cliente}", styles['Normal']))
        elements.append(Paragraph(f"<b>Dispositivo:</b> {sale.device}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha Venta:</b> {sale.fecha_venta}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Schedule Table
        data = [['Cuota', 'Fecha', 'Monto', 'Estado']]
        for cuota in sale.installments.all():
            estado = "Pagado" if cuota.pagado else "Pendiente"
            data.append([str(cuota.numero), str(cuota.fecha_vencimiento), f"S/ {cuota.monto}", estado])
        
        table = Table(data, colWidths=[50, 150, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Summary
        total_cuotas = sale.installments.count()
        pagadas = sale.installments.filter(pagado=True).count()
        pendientes = total_cuotas - pagadas
        monto_pagado = sum(c.monto for c in sale.installments.filter(pagado=True))
        monto_pendiente = sum(c.monto for c in sale.installments.filter(pagado=False))

        elements.append(Paragraph("<b>RESUMEN</b>", styles['Heading2']))
        elements.append(Paragraph(f"Total de Cuotas: {total_cuotas}", styles['Normal']))
        elements.append(Paragraph(f"Cuotas Pagadas: {pagadas}", styles['Normal']))
        elements.append(Paragraph(f"Cuotas Pendientes: {pendientes}", styles['Normal']))
        elements.append(Paragraph(f"Monto Pagado: S/ {monto_pagado:.2f}", styles['Normal']))
        elements.append(Paragraph(f"Monto Pendiente: S/ {monto_pendiente:.2f}", styles['Normal']))

        doc.build(elements)
        return response

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
