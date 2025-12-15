from rest_framework import viewsets
from .models import ContratoMoto, CuotaContrato
from .serializers import ContratoMotoSerializer, CuotaContratoSerializer

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import ContratoMoto, CuotaContrato
from .serializers import ContratoMotoSerializer, CuotaContratoSerializer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from datetime import date

class ContratoMotoViewSet(viewsets.ModelViewSet):
    queryset = ContratoMoto.objects.select_related('cliente', 'moto').all()
    serializer_class = ContratoMotoSerializer

    @action(detail=True, methods=['get'])
    def download_schedule_pdf(self, request, pk=None):
        contrato = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"calendario_pagos_{contrato.cliente.nombres}_{contrato.cliente.apellidos}.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Calendario de Pagos - Venta Moto - {contrato.cliente.nombres} {contrato.cliente.apellidos}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Details
        elements.append(Paragraph(f"<b>Cliente:</b> {contrato.cliente}", styles['Normal']))
        elements.append(Paragraph(f"<b>Moto:</b> {contrato.moto}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {contrato.fecha_contrato}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Schedule Table
        data = [['Cuota', 'Fecha', 'Monto', 'Estado']]
        for cuota in contrato.cuotas.all():
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
        total_cuotas = contrato.cuotas.count()
        pagadas = contrato.cuotas.filter(pagado=True).count()
        pendientes = total_cuotas - pagadas
        monto_pagado = sum(c.monto for c in contrato.cuotas.filter(pagado=True))
        monto_pendiente = sum(c.monto for c in contrato.cuotas.filter(pagado=False))

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
        contrato = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        filename = f"contrato_legal_{contrato.cliente.nombres}_{contrato.cliente.apellidos}.pdf".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph("CONTRATO DE ALQUILER VENTA DE VEHÍCULO", styles['Title']))
        elements.append(Spacer(1, 12))

        # Body Text
        # Calculate values
        inicial = contrato.monto_inicial
        restante_con_interes = contrato.monto_total_deuda
        total_con_interes = inicial + restante_con_interes
        cuota_diaria = contrato.monto_cuota
        fecha_actual = date.today().strftime("%d/%m/%Y")
        
        # Format currency
        def money(val):
            return f"S/ {val:.2f}"

        text_content = f"""
        Conste por el presente contrato de alquiler venta de vehículo nuevo (00 km) que celebran de una parte Robert David Quispe de la Cruz, identificado con DNI 44749079 y Angelly Leslie Santiago Salomón, identificada con DNI 47926921, domiciliados en Calle Flor de Jara Mz. J Lt. 9B, Urbanización Villa Santa Anita, Distrito de Santa Anita, a quienes en adelante se le denominará LOS VENDEDORES, y de otra parte <b>{contrato.cliente.nombres} {contrato.cliente.apellidos}</b> identificado con DNI <b>{contrato.cliente.dni}</b> domiciliado en <b>{contrato.cliente.domicilio}</b>, a quien en adelante se le denominará como EL COMPRADOR , el mismo que se extiende en los términos y condiciones siguientes:<br/><br/>
        
        PRIMERO. - LOS VENDEDORES son propietarios del vehículo de marca <b>{contrato.moto.marca}</b>, modelo <b>{contrato.moto.modelo}</b>, con número de motor <b>{contrato.moto.numero_motor}</b>, placa <b>{contrato.moto.placa}</b>, número de serie <b>{contrato.moto.numero_serie}</b>, color <b>{contrato.moto.color}</b>, año <b>{contrato.moto.anio}</b><br/><br/>
        
        SEGUNDO. - Por el presente contrato LOS VENDEDORES dan en Alquiler-Venta el vehículo descrito en la primera cláusula al COMPRADOR, en la suma de <b>{money(total_con_interes)}</b>, suma que es pagada de la siguiente manera: EL COMPRADOR hace entrega de un adelanto como cuota inicial de <b>{money(inicial)}</b> , faltando cancelar <b>{money(restante_con_interes)}</b>.<br/>
        -Pago Diario: <b>{money(cuota_diaria)}</b> diarios, sin ser contados los días domingos. El pago será efectuado hasta completar la suma ascendiente a <b>{money(restante_con_interes)}</b>, a partir del día <b>{contrato.fecha_contrato.strftime("%d/%m/%Y")}</b>. Por cada pago, LOS VENDEDORES extenderán el recibo correspondiente.<br/><br/>
        
        TERCERO. - Queda establecido que a partir del día <b>{contrato.fecha_contrato.strftime("%d/%m/%Y")}</b>, si el vehículo materia del presente contrato sufriera cualquier desperfecto mecánico o siniestro EL COMPRADOR asumirá el total del costo que este genere, comunicando a LOS VENDEDORES<br/><br/>
        
        CUARTO. - EL COMPRADOR se hará responsable de su mantenimiento y funcionamiento. En caso de robo del vehículo EL COMPRADOR se hará responsable de cumplir con los pagos diarios hasta completar el total pactado.<br/><br/>
        
        QUINTO. - En caso que el comprador incumpliese con el pago diario por un lapso de 2 semanas consecutivas o no injustificadas quedará sin efecto el presente contrato , estando obligado EL COMPRADOR a devolver el vehículo a LOS VENDEDORES, perdiendo el monto cancelado hasta la fecha del incumplimiento, siendo devuelto en las mismas condiciones como lo recibe EL COMPRADOR<br/><br/>
        
        SEXTO. - Ambas partes declaran que entre el precio pactado y el vehículo materia de venta existe la más justa y perfecta equivalencia no teniendo nada que reclamarse al respecto , así como que el bien se trata de un vehículo nuevo (00 km). El costo del mantenimiento del vehículo lo asumirá EL COMPRADOR, con la supervisión de LOS VENDEDORES. EL COMPRADOR se compromete a entregar todos los recibos o boletas del costo por cambios adherentes a LOS VENDEDORES<br/><br/>
        
        SÉPTIMO. - EL COMPRADOR declara que recibe el vehículo a su entera satisfacción , el mismo que es nuevo (00 km) y precisa que se encuentra con sus accesorios completos, así como funcionando en forma adecuada.<br/><br/>
        
        OCTAVO. - Ambas partes dejan constancia que es de cuenta y responsabilidad de LOS VENDEDORES, cualquier multa, infracción, medida judicial y extra judicial que pueda tener el vehículo hasta el momento de la firma del presente contrato , que se realiza el día <b>{fecha_actual}</b> , encontrándose obligado a su saneamiento de ley en caso de que hubiese, así como EL COMPRADOR se hará responsable de los mismos términos a partir del presente contrato.<br/><br/>
        
        NOVENO. - Queda expresamente convenido que en el caso que EL COMPRADOR desee rescindir el presente contrato antes de su vencimiento, deberá entregar el vehículo en las mismas condiciones como le fue entregado y perderá el total del monto abonado hasta esa fecha, incluyendo los gastos adicionales<br/><br/>
        
        DÉCIMO. - LOS VENDEDORES se comprometen a hacer los trámites necesarios para la transferencia a favor del COMPRADOR luego de cancelar el monto pactado , siendo este último quien asumirá los gastos que suscite el trámite correspondiente.<br/><br/>
        """

        elements.append(Paragraph(text_content, styles['Normal']))
        elements.append(Spacer(1, 48))

        # Signatures
        # Using a table for signatures to align them
        sig_data = [
            ['“LOS VENDEDORES”', '“LOS VENDEDORES”', '“EL COMPRADOR”'],
            ['', '', ''],
            ['------------------------------', '------------------------------', '------------------------------'],
            ['Robert David Quispe de la Cruz', 'Leslie Angely Santiago Salomón', f'{contrato.cliente.nombres} {contrato.cliente.apellidos}'],
            ['DNI: 44749379', 'DNI: 47926921', f'DNI: {contrato.cliente.dni}']
        ]
        
        sig_table = Table(sig_data)
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 24), # Space for signature
        ]))
        elements.append(sig_table)

        doc.build(elements)
        return response

class CuotaContratoViewSet(viewsets.ModelViewSet):
    queryset = CuotaContrato.objects.select_related('contrato__cliente').all()
    serializer_class = CuotaContratoSerializer

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
        
        contrato = cuota.contrato
        if not contrato.cuotas.filter(pagado=False).exists():
            contrato.estado = 'Pagado'
        else:
            contrato.estado = 'Activo'
        contrato.save()

        return Response(CuotaContratoSerializer(cuota).data)

    def perform_update(self, serializer):
        cuota = serializer.save()
        contrato = cuota.contrato
        if not contrato.cuotas.filter(pagado=False).exists():
            contrato.estado = 'Pagado'
        else:
            contrato.estado = 'Activo'
        contrato.save()
