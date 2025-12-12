from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from users.models import Client
from inventory.models import Moto
from loans.models import Prestamo, CuotaPrestamo
from contracts.models import ContratoMoto, CuotaContrato
from datetime import date

from devices.models import Device, DeviceSale, DeviceInstallment

class DashboardMetricsView(APIView):
    def get(self, request):
        total_prestado = Prestamo.objects.aggregate(Sum('monto_prestado'))['monto_prestado__sum'] or 0
        total_vendido_motos = Moto.objects.filter(estado='Vendida').aggregate(Sum('precio'))['precio__sum'] or 0
        
        # Device Sales (Sum of prices of sold devices)
        total_vendido_devices = Device.objects.filter(estado='Vendido').aggregate(Sum('precio'))['precio__sum'] or 0

        today = date.today()
        cuotas_vencidas_prestamos = CuotaPrestamo.objects.filter(fecha_vencimiento__lt=today, pagado=False).count()
        cuotas_vencidas_contratos = CuotaContrato.objects.filter(fecha_vencimiento__lt=today, pagado=False).count()
        # Add device installments overdue
        cuotas_vencidas_devices = DeviceInstallment.objects.filter(fecha_vencimiento__lt=today, pagado=False).count()
        
        total_vencidas = cuotas_vencidas_prestamos + cuotas_vencidas_contratos + cuotas_vencidas_devices

        motos_disponibles = Moto.objects.filter(estado='Disponible').count()
        motos_ocupadas = Moto.objects.filter(estado__in=['Alquilada', 'Vendida']).count()
        
        devices_disponibles = Device.objects.filter(estado='Disponible').count()
        devices_vendidos = Device.objects.filter(estado='Vendido').count()

        total_clientes = Client.objects.count()
        prestamos_activos = Prestamo.objects.count() 
        contratos_activos = ContratoMoto.objects.count()
        ventas_celulares_activas = DeviceSale.objects.filter(estado='Activo').count()

        # Recent Activity 
        recent_loans = Prestamo.objects.order_by('-fecha_inicio')[:5]
        recent_contracts = ContratoMoto.objects.order_by('-fecha_contrato')[:5]
        recent_device_sales = DeviceSale.objects.order_by('-fecha_venta')[:5]
        
        recent_activity = []
        for loan in recent_loans:
            recent_activity.append({
                'type': 'Préstamo',
                'id': loan.id,
                'client': f"{loan.cliente.nombres} {loan.cliente.apellidos}",
                'amount': loan.monto_prestado,
                'date': loan.fecha_inicio
            })
        
        for contract in recent_contracts:
            recent_activity.append({
                'type': 'Contrato',
                'id': contract.id,
                'client': f"{contract.cliente.nombres} {contract.cliente.apellidos}",
                'amount': contract.monto_inicial,
                'date': contract.fecha_contrato
            })
            
        for sale in recent_device_sales:
             recent_activity.append({
                'type': 'Venta Celular',
                'id': sale.id,
                'client': f"{sale.cliente.nombres} {sale.cliente.apellidos}",
                'amount': sale.device.precio, # Use device price or initial amount
                'date': sale.fecha_venta
            })
        
        # Sort combined list by date desc and take top 5
        recent_activity.sort(key=lambda x: x['date'], reverse=True)
        recent_activity = recent_activity[:5]

        # Income History (Last 6 months)
        income_history = []
        for i in range(5, -1, -1):
            month_date = today.replace(day=1) 
            year = month_date.year
            month = month_date.month - i
            while month <= 0:
                month += 12
                year -= 1
            
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            # Sum payments
            loans_income = CuotaPrestamo.objects.filter(
                fecha_pago__gte=start_date, 
                fecha_pago__lt=end_date, 
                pagado=True
            ).aggregate(Sum('monto'))['monto__sum'] or 0
            
            contracts_income = CuotaContrato.objects.filter(
                fecha_pago__gte=start_date, 
                fecha_pago__lt=end_date, 
                pagado=True
            ).aggregate(Sum('monto'))['monto__sum'] or 0
            
            devices_income = DeviceInstallment.objects.filter(
                fecha_pago__gte=start_date, 
                fecha_pago__lt=end_date, 
                pagado=True
            ).aggregate(Sum('monto'))['monto__sum'] or 0
            
            # Add initial payments for device sales in this month
            devices_initial_income = DeviceSale.objects.filter(
                fecha_venta__gte=start_date,
                fecha_venta__lt=end_date
            ).aggregate(Sum('monto_inicial'))['monto_inicial__sum'] or 0
            
            # And full payments for cash sales? (DeviceSale cash sales have monto_inicial = price usually? or we handle it differently?)
            # In DeviceSale model: if type='Contado', monto_total_deuda=0. We should check if we store the full price somewhere as income.
            # Assuming 'monto_inicial' captures the down payment. For 'Contado', let's assume the frontend sends the price as monto_inicial or we need to check logic.
            # Looking at DeviceSales.jsx:
            # For 'Contado', we don't send monto_inicial. We just save.
            # Wait, DeviceSale model save() logic:
            # if type == 'Contado': cuotas=0, estado='Pagado'. 
            # It doesn't seem to set monto_inicial explicitly to price.
            # Let's fix this in the view logic: Sum price for Contado sales + monto_inicial for Credito sales.
            
            devices_cash_income = DeviceSale.objects.filter(
                fecha_venta__gte=start_date,
                fecha_venta__lt=end_date,
                tipo='Contado'
            ).count() # This is a count, I need sum of device prices.
            
            # Efficient way:
            devices_cash_value = 0
            cash_sales = DeviceSale.objects.filter(
                 fecha_venta__gte=start_date,
                 fecha_venta__lt=end_date,
                 tipo='Contado'
            ).select_related('device')
            
            for s in cash_sales:
                devices_cash_value += s.device.precio
            
            total_devices_income = devices_income + devices_initial_income + devices_cash_value

            spanish_months = {
                1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
            }
            
            income_history.append({
                'name': spanish_months[month],
                'prestamos': loans_income,
                'contratos': contracts_income,
                'devices': total_devices_income,
                'total': loans_income + contracts_income + total_devices_income
            })

        # Portfolio Distribution
        active_loans = Prestamo.objects.filter(estado='Activo').count()
        active_contracts = ContratoMoto.objects.filter(estado='Activo').count()
        
        portfolio_distribution = [
            {'name': 'Préstamos', 'value': active_loans},
            {'name': 'Contratos', 'value': active_contracts},
            {'name': 'Celulares', 'value': ventas_celulares_activas}
        ]

        # Moto Status for Chart
        moto_status_data = [
            {'name': 'Disponibles', 'value': motos_disponibles},
            {'name': 'Ocupadas', 'value': motos_ocupadas}
        ]
        
        # Device Status for Chart
        device_status_data = [
            {'name': 'Disponibles', 'value': devices_disponibles},
            {'name': 'Vendidos', 'value': devices_vendidos}
        ]

        return Response({
            'total_prestado': total_prestado,
            'total_vendido_motos': total_vendido_motos,
            'total_vendido_devices': total_vendido_devices,
            'cuotas_vencidas_hoy': total_vencidas,
            'motos_disponibles': motos_disponibles,
            'motos_ocupadas': motos_ocupadas,
            'devices_disponibles': devices_disponibles,
            'devices_vendidos': devices_vendidos,
            'total_clientes': total_clientes,
            'prestamos_activos': prestamos_activos,
            'contratos_activos': contratos_activos,
            'ventas_celulares_activas': ventas_celulares_activas,
            'recent_activity': recent_activity,
            'income_history': income_history,
            'portfolio_distribution': portfolio_distribution,
            'moto_status_data': moto_status_data,
            'device_status_data': device_status_data
        })
