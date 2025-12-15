from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date
from .models import Device, DeviceSale, DeviceInstallment
from .serializers import DeviceSerializer, DeviceSaleSerializer, DeviceInstallmentSerializer
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
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
        # Generate Schedule PDF
        sale = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"venta_celular_{sale.cliente.nombres}_{sale.cliente.apellidos}.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Calendario de Pagos - Venta Celular - {sale.cliente.nombres} {sale.cliente.apellidos}", styles['Title']))
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

    @action(detail=True, methods=['get'])
    def download_contract_pdf(self, request, pk=None):
        sale = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"contrato_celular_{sale.cliente.nombres}_{sale.cliente.apellidos}.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Helper for currency
        def money(val):
            return f"{val:.2f}"

        # Dates
        day = date.today().day
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        month_name = months[date.today().month - 1]
        year = date.today().year

        # Title
        elements.append(Paragraph("CONTRATO PRIVADO DE COMPRAVENTA DE TELÉFONO MÓVIL A PLAZOS", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"En la ciudad de Lima, a los {day} días del mes de {month_name} de {year}.", styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>REUNIDOS</b>", styles['Heading4']))
        elements.append(Spacer(1, 6))

        # Parties
        seller_text = "<b>DE UNA PARTE:</b> JHAMIR QUISPE SANTIAGO, en calidad de VENDEDOR, identificado con DNI N° 61027309, con domicilio en Urb. Villa Santa Anita, Flor de Jara Mz J Lt 9B."
        buyer_text = f"<b>Y DE LA OTRA PARTE:</b> {sale.cliente.nombres} {sale.cliente.apellidos}, en calidad de COMPRADOR, identificado con DNI N° {sale.cliente.dni}, con domicilio en {sale.cliente.domicilio}."
        
        elements.append(Paragraph(seller_text, styles['Normal']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(buyer_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Ambas partes se reconocen mutuamente plena capacidad legal para el otorgamiento del presente contrato y, a tal efecto,", styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>EXPONEN:</b>", styles['Heading4']))
        elements.append(Spacer(1, 6))

        # Device Details
        device = sale.device
        elements.append(Paragraph("I. Que EL VENDEDOR es propietario legítimo del teléfono móvil con las siguientes características:", styles['Normal']))
        elements.append(Spacer(1, 6))
        
        details = [
            f"<b>Marca:</b> {device.marca}",
            f"<b>Modelo:</b> {device.modelo}",
            f"<b>Color:</b> {device.color}",
            f"<b>IMEI 1:</b> {device.imei}",
            f"<b>IMEI 2:</b> {device.imei2 if device.imei2 else 'N/A'}",
            f"<b>Número de Serie:</b> {device.numero_serie}",
        ]
        for d in details:
            elements.append(Paragraph(d, styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("II. Que EL VENDEDOR declara que el equipo es un producto original, adquirido de forma lícita y libre de cargas o gravámenes.", styles['Normal']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("III. Que habiendo convenido la venta del bien reseñado, ambas partes formalizan el presente acuerdo regido por las siguientes:", styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>CLÁUSULAS:</b>", styles['Heading4']))
        elements.append(Spacer(1, 6))

        # Clauses
        elements.append(Paragraph("<b>PRIMERA: OBJETO DEL CONTRATO</b> EL VENDEDOR transfiere en venta real y enajenación perpetua a favor de EL COMPRADOR el teléfono móvil descrito en el apartado I de la exposición, por el precio y condiciones que se detallan a continuación.", styles['Normal']))
        elements.append(Spacer(1, 6))

        total_price = float(sale.monto_inicial) + float(sale.monto_total_deuda if sale.monto_total_deuda else 0)
        
        elements.append(Paragraph(f"<b>SEGUNDA: PRECIO Y FORMA DE PAGO</b> El precio total pactado por la compraventa asciende a la suma de S/ {money(total_price)}, el cual incluye los intereses por financiamiento acordado. La forma de pago se realizará de la siguiente manera:", styles['Normal']))
        elements.append(Spacer(1, 6))
        
        elements.append(Paragraph(f"<b>CUOTA INICIAL:</b> EL COMPRADOR entrega en este acto la suma de S/ {money(sale.monto_inicial)} a EL VENDEDOR, quien declara recibirla a su entera satisfacción, sirviendo el presente documento como constancia de recibo.", styles['Normal']))
        elements.append(Spacer(1, 6))

        if sale.tipo == 'Credito':
            elements.append(Paragraph(f"<b>SALDO RESTANTE:</b> El saldo restante de S/ {money(sale.monto_total_deuda)} será cancelado mediante PAGOS {sale.metodo_pago.upper()}S.", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<b>CRONOGRAMA DE PAGOS:</b> EL COMPRADOR se compromete a pagar {sale.cuotas_totales} cuotas {sale.metodo_pago.lower()}s consecutivas de S/ {money(sale.monto_cuota)} cada una.", styles['Normal']))
            elements.append(Spacer(1, 6))
            
            # Try to get first installment date
            first_installment = sale.installments.order_by('numero').first()
            first_date = first_installment.fecha_vencimiento.strftime("%d/%m/%Y") if first_installment else "___________"
            
            elements.append(Paragraph(f"El primer pago {sale.metodo_pago.lower()} se realizará el día: {first_date}.", styles['Normal']))
        else:
             elements.append(Paragraph("<b>SALDO RESTANTE:</b> Cancelado al contado.", styles['Normal']))

        elements.append(Spacer(1, 6))
        elements.append(Paragraph("El medio de pago será: (Efectivo / Yape / Plin / Transferencia).", styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("<b>TERCERA: ENTREGA Y ESTADO DEL BIEN</b> En este acto, EL VENDEDOR hace entrega física del equipo a EL COMPRADOR. EL COMPRADOR declara recibir el equipo revisado y conforme, salvo los vicios ocultos cubiertos en las garantías estipuladas más adelante.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>CUARTA: INCUMPLIMIENTO DE PAGO</b> El incumplimiento en el pago de dos (2) cuotas semanales consecutivas o alternadas dará derecho a EL VENDEDOR a dar por resuelto el contrato, pudiendo exigir la devolución inmediata del equipo y reteniendo el 30% del monto total abonado hasta la fecha en concepto de penalidad por uso y daños y perjuicios.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>QUINTA: GARANTÍA DE ORIGINALIDAD</b> EL VENDEDOR garantiza que el producto es original. En caso de comprobarse que el equipo es una réplica o falsificación, EL VENDEDOR se obliga a devolver la totalidad del dinero recibido en un plazo no mayor a 30 días calendario desde la fecha de este contrato, contra la devolución del equipo.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>SEXTA: GARANTÍA DE SOFTWARE Y BLOQUEO</b><br/><b>Software:</b> EL VENDEDOR asegura que el software es original y no ha sido modificado (Root/Jailbreak). Si EL COMPRADOR descubre modificaciones preexistentes, tiene un plazo de 7 días para solicitar la resolución del contrato y la devolución del dinero.<br/><b>IMEI:</b> EL VENDEDOR garantiza que el equipo no proviene de actividades ilícitas. En caso de que el equipo sea bloqueado por reporte de robo, pérdida o deuda anterior a la fecha de venta, EL VENDEDOR se obliga a devolver la totalidad del dinero recibido dentro de los 30 días siguientes a la firma del presente.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>SÉPTIMA: GARANTÍA DE FUNCIONAMIENTO</b> EL COMPRADOR cuenta con un periodo de prueba de siete (7) días calendario para verificar el correcto funcionamiento de: Wi-Fi, cámaras, micrófono, altavoces, señal, Bluetooth, GPS y pantalla táctil. Si se detectaran fallas en estos componentes dentro de dicho plazo (no atribuibles al mal uso), EL VENDEDOR devolverá la cantidad pactada contra la entrega del equipo.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>OCTAVA: EXCLUSIONES DE GARANTÍA</b> La garantía otorgada por EL VENDEDOR queda anulada automáticamente si el equipo sufre deterioro, rotura de pantalla, ingreso de líquidos, golpes o cualquier desperfecto derivado del mal uso, negligencia o manipulación indebida por parte de EL COMPRADOR posterior a la entrega.", styles['Normal']))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph("<b>NOVENA: LEY APLICABLE Y JURISDICCIÓN</b> Para todo lo no previsto en este contrato, se aplicará la normativa del Código Civil Peruano vigente. Para cualquier controversia que pudiera derivarse del presente documento, ambas partes se someten a la jurisdicción de los Jueces y Tribunales de la ciudad de Lima.", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Signatures Block
        signature_elements = []
        signature_elements.append(Paragraph("Estando conformes con el contenido, firman el presente contrato por duplicado, a un solo efecto y valor legal.", styles['Normal']))
        signature_elements.append(Spacer(1, 48))

        # Signatures
        sig_data = [
            ['EL VENDEDOR', '', 'EL COMPRADOR'],
            ['', '', ''],
            ['------------------------------', '', '------------------------------'],
            ['JHAMIR QUISPE SANTIAGO', '', f'{sale.cliente.nombres} {sale.cliente.apellidos}'],
            ['DNI: 61027309', '', f'DNI: {sale.cliente.dni}']
        ]
        
        sig_table = Table(sig_data)
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 24),
        ]))
        signature_elements.append(sig_table)
        
        elements.append(KeepTogether(signature_elements))


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
