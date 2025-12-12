from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date
from django.http import HttpResponse
from .models import Prestamo, CuotaPrestamo
from .serializers import PrestamoSerializer, CuotaPrestamoSerializer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        prestamo = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"prestamo_{prestamo.cliente.nombres}_{prestamo.cliente.apellidos}.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Cronograma de Pagos - Préstamo #{prestamo.id}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Details
        elements.append(Paragraph(f"<b>Cliente:</b> {prestamo.cliente}", styles['Normal']))
        elements.append(Paragraph(f"<b>Monto Prestado:</b> S/ {prestamo.monto_prestado}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {prestamo.fecha_inicio}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Schedule Table
        data = [['Cuota', 'Fecha                                                                     ', 'Monto             ', 'Estado            ']]
        for cuota in prestamo.cuotas.all():
            estado = "Pagado" if cuota.pagado else "Pendiente"
            data.append([str(cuota.numero), str(cuota.fecha_vencimiento), str(cuota.monto), estado])
        
        table = Table(data)
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
        total_cuotas = prestamo.cuotas.count()
        pagadas = prestamo.cuotas.filter(pagado=True).count()
        pendientes = total_cuotas - pagadas
        monto_pagado = sum(c.monto for c in prestamo.cuotas.filter(pagado=True))
        monto_pendiente = sum(c.monto for c in prestamo.cuotas.filter(pagado=False))

        elements.append(Paragraph("<b>RESUMEN</b>", styles['Heading2']))
        elements.append(Paragraph(f"Total de Cuotas: {total_cuotas}", styles['Normal']))
        elements.append(Paragraph(f"Cuotas Pagadas: {pagadas}", styles['Normal']))
        elements.append(Paragraph(f"Cuotas Pendientes: {pendientes}", styles['Normal']))
        elements.append(Paragraph(f"Monto Pagado: S/ {monto_pagado:.2f}", styles['Normal']))
        elements.append(Paragraph(f"Monto Pendiente: S/ {monto_pendiente:.2f}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Important Notes
        elements.append(Paragraph("<b>NOTAS IMPORTANTES</b>", styles['Heading2']))
        notes = [
            "• Este calendario muestra las fechas de vencimiento de cada cuota.",
            "• Es importante realizar los pagos en las fechas indicadas.",
            "• En caso de retraso, pueden aplicarse intereses adicionales.",
            "• Para cualquier consulta, contacte con nosotros."
        ]
        for note in notes:
            elements.append(Paragraph(note, styles['Normal']))
            elements.append(Spacer(1, 6))

        doc.build(elements)
        return response

class CuotaPrestamoViewSet(viewsets.ModelViewSet):
    queryset = CuotaPrestamo.objects.all()
    serializer_class = CuotaPrestamoSerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        cuota = self.get_object()
        monto_pago = float(request.data.get('monto', 0))
        metodo = request.data.get('metodo_pago', 'Efectivo')

        if monto_pago <= 0:
            return Response({'error': 'Monto inválido'}, status=400)

        cuota.monto_pagado = float(cuota.monto_pagado) + monto_pago
        cuota.metodo_pago = metodo
        
        # Check if fully paid (allow small margin of error for decimals if needed, but strict for now)
        if cuota.monto_pagado >= float(cuota.monto):
            cuota.pagado = True
            cuota.fecha_pago = date.today()
        
        cuota.save()
        
        # Update Loan Status
        prestamo = cuota.prestamo
        if not prestamo.cuotas.filter(pagado=False).exists():
            prestamo.estado = 'Pagado'
        else:
            prestamo.estado = 'Activo'
        prestamo.save()

        return Response(CuotaPrestamoSerializer(cuota).data)

    def perform_update(self, serializer):
        # Keep this for standard updates if needed, but 'pay' action is preferred for payments
        cuota = serializer.save()
        prestamo = cuota.prestamo
        if not prestamo.cuotas.filter(pagado=False).exists():
            prestamo.estado = 'Pagado'
        else:
            prestamo.estado = 'Activo'
        prestamo.save()
