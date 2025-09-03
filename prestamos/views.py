from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from .forms import PrestamoForm, ClienteForm
from .models import Prestamo, Cliente, CuotaPago
from datetime import datetime, timedelta, date
import calendar
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
# Create your views here.

def home(request): 
    return render(request, 'home.html')

def signup(request): 
    # Solo usuarios autenticados pueden crear nuevos usuarios
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # No hacer login automático, solo crear el usuario
                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                return redirect('index')
            except Exception as e:
                return render(request, 'signup.html', {
                    "form": form, 
                    "error": "Error al crear el usuario. Inténtalo de nuevo."
                })
        else:
            # Si el formulario no es válido, mostrar errores
            return render(request, 'signup.html', {
                "form": form, 
                "error": "Por favor, corrige los errores en el formulario."
            }) 

def index(request):
    # Solo usuarios autenticados pueden ver el panel
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Obtener parámetro de búsqueda
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Buscar por nombre del cliente
        prestamos = Prestamo.objects.filter(cliente__nombre__icontains=search_query)
    else:
        prestamos = Prestamo.objects.all()

    return render(request, 'index.html', {
        'prestamos': prestamos,
        'search_query': search_query
    })

def crear_prestamo(request):
    # Solo usuarios autenticados pueden crear préstamos
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'GET':
        return render(request, 'crear_prestamos.html', {'form': PrestamoForm()})
    else:
        form = PrestamoForm(request.POST)
        if form.is_valid():
            try:
                prestamo = form.save()
                # Generar cuotas automáticamente
                prestamo.generar_cuotas()
                messages.success(request, f'Préstamo de ${prestamo.monto} creado exitosamente para {prestamo.cliente.nombre}. Se han generado las cuotas automáticamente.')
                return redirect('index')
            except Exception as e:
                return render(request, 'crear_prestamos.html', {
                    "form": form, 
                    "error": "Error al crear el préstamo. Inténtalo de nuevo."
                })
        else:
            return render(request, 'crear_prestamos.html', {
                "form": form, 
                "error": "Por favor, corrige los errores en el formulario."
            })

def registrar_cliente(request):
    # Solo usuarios autenticados pueden registrar clientes
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'GET':
        return render(request, 'registrar_cliente.html', {'form': ClienteForm()})
    else:
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                cliente = form.save()
                messages.success(request, f'Cliente {cliente.nombre} registrado exitosamente.')
                return redirect('index')
            except Exception as e:
                return render(request, 'registrar_cliente.html', {
                    "form": form, 
                    "error": "Error al registrar el cliente. Inténtalo de nuevo."
                })
        else:
            return render(request, 'registrar_cliente.html', {
                "form": form, 
                "error": "Por favor, corrige los errores en el formulario."
            })

def registrar_prestamo(request):
    # Solo usuarios autenticados pueden registrar préstamos
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'GET':
        return render(request, 'registrar_prestamo.html', {'form': PrestamoForm()})
    else:
        form = PrestamoForm(request.POST)
        if form.is_valid():
            try:
                prestamo = form.save()
                # Generar cuotas automáticamente
                prestamo.generar_cuotas()
                messages.success(request, f'Préstamo de ${prestamo.monto} registrado exitosamente para {prestamo.cliente.nombre}. Se han generado las cuotas automáticamente.')
                return redirect('index')
            except Exception as e:
                return render(request, 'registrar_prestamo.html', {
                    "form": form, 
                    "error": "Error al registrar el préstamo. Inténtalo de nuevo."
                })
        else:
            return render(request, 'registrar_prestamo.html', {
                "form": form, 
                "error": "Por favor, corrige los errores en el formulario."
            })

def calendario_pagos(request, prestamo_id):
    # Solo usuarios autenticados pueden ver el calendario
    if not request.user.is_authenticated:
        return redirect('signin')
    
    try:
        prestamo = Prestamo.objects.get(id=prestamo_id)
    except Prestamo.DoesNotExist:
        messages.error(request, 'Préstamo no encontrado.')
        return redirect('index')
    
    # Generar cuotas si no existen
    if not prestamo.cuotas.exists():
        prestamo.generar_cuotas()
    
    # Obtener el mes y año actual
    now = datetime.now()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)
    
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        month = now.month
        year = now.year
    
    # Validar rango de meses (1-12)
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Generar el calendario
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Obtener todas las cuotas del préstamo
    cuotas = prestamo.cuotas.all().order_by('fecha_pago')
    
    context = {
        'prestamo': prestamo,
        'calendar': cal,
        'month_name': month_name,
        'month': month,
        'year': year,
        'cuotas': cuotas,
        'now': now,
    }
    
    return render(request, 'calendario_pagos.html', context)

def eliminar_prestamo(request, prestamo_id):
    """Elimina un préstamo y todas sus cuotas"""
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'POST':
        try:
            prestamo = Prestamo.objects.get(id=prestamo_id)
            cliente_nombre = prestamo.cliente.nombre
            prestamo.delete()  # Esto también eliminará las cuotas por CASCADE
            messages.success(request, f'Préstamo de {cliente_nombre} eliminado exitosamente.')
        except Prestamo.DoesNotExist:
            messages.error(request, 'Préstamo no encontrado.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el préstamo: {str(e)}')
    else:
        messages.error(request, 'Método no permitido.')
    
    return redirect('index')

def cancelar_prestamo(request, prestamo_id):
    """Cancela un préstamo marcándolo como cancelado"""
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'POST':
        try:
            prestamo = Prestamo.objects.get(id=prestamo_id)
            prestamo.estado = True  # True = cancelado
            prestamo.save()
            messages.success(request, f'Préstamo de {prestamo.cliente.nombre} cancelado exitosamente.')
        except Prestamo.DoesNotExist:
            messages.error(request, 'Préstamo no encontrado.')
    
    return redirect('calendario_pagos', prestamo_id=prestamo_id)

def marcar_cuota_pagada(request, cuota_id):
    """Marca una cuota como pagada"""
    if not request.user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'POST':
        try:
            cuota = CuotaPago.objects.get(id=cuota_id)
            cuota.pagada = True
            cuota.fecha_pagada = datetime.now().date()
            cuota.save()
            messages.success(request, f'Cuota de ${cuota.monto} marcada como pagada.')
        except CuotaPago.DoesNotExist:
            messages.error(request, 'Cuota no encontrada.')
    
    # Redirigir de vuelta al calendario
    return redirect('calendario_pagos', prestamo_id=cuota.prestamo.id)

def signout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

def reporte_pagos(request):
    """Muestra un reporte de pagos semanales que vencen hoy"""
    # Solo usuarios autenticados pueden ver el reporte
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Obtener la fecha actual
    hoy = date.today()
    
    # Buscar cuotas semanales que vencen hoy y no han sido pagadas
    cuotas_vencidas_hoy = CuotaPago.objects.filter(
        fecha_pago=hoy,
        tipo_cuota='semanal',
        pagada=False
    ).select_related('prestamo__cliente').order_by('prestamo__cliente__nombre')
    
    # Calcular totales
    total_cuotas = cuotas_vencidas_hoy.count()
    total_monto = sum(cuota.monto for cuota in cuotas_vencidas_hoy)
    
    # Obtener estadísticas adicionales
    prestamos_semanal_activos = Prestamo.objects.filter(
        forma_pago='semanal',
        estado=False
    ).count()
    
    cuotas_pagadas_hoy = CuotaPago.objects.filter(
        fecha_pago=hoy,
        tipo_cuota='semanal',
        pagada=True
    ).count()
    
    context = {
        'cuotas_vencidas_hoy': cuotas_vencidas_hoy,
        'total_cuotas': total_cuotas,
        'total_monto': total_monto,
        'prestamos_semanal_activos': prestamos_semanal_activos,
        'cuotas_pagadas_hoy': cuotas_pagadas_hoy,
        'fecha_hoy': hoy,
    }
    
    return render(request, 'reporte_pagos.html', context)

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            # Usuario o contraseña incorrectos
            return render(request, 'signin.html', {
                'form': AuthenticationForm(), 
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            # Usuario autenticado correctamente
            login(request, user)
            return redirect('index')

def descargar_calendario_pdf(request, prestamo_id):
    """Genera y descarga un PDF con el calendario de pagos del préstamo"""
    # Solo usuarios autenticados pueden descargar calendarios
    if not request.user.is_authenticated:
        return redirect('signin')
    
    try:
        prestamo = Prestamo.objects.get(id=prestamo_id)
    except Prestamo.DoesNotExist:
        messages.error(request, 'Préstamo no encontrado.')
        return redirect('index')
    
    # Generar cuotas si no existen
    if not prestamo.cuotas.exists():
        prestamo.generar_cuotas()
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.darkgreen
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("CALENDARIO DE PAGOS", title_style))
    story.append(Spacer(1, 12))
    
    # Información del préstamo
    story.append(Paragraph(f"<b>Cliente:</b> {prestamo.cliente.nombre}", styles['Normal']))
    story.append(Paragraph(f"<b>Email:</b> {prestamo.cliente.email}", styles['Normal']))
    story.append(Paragraph(f"<b>Teléfono:</b> {prestamo.cliente.telefono}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto del Préstamo:</b> ${prestamo.monto:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Total a Pagar:</b> ${prestamo.monto_total:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Forma de Pago:</b> {prestamo.get_forma_pago_display()}", styles['Normal']))
    story.append(Paragraph(f"<b>Fecha de Préstamo:</b> {prestamo.fecha_prestamo.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph(f"<b>Fecha de Vencimiento:</b> {prestamo.fecha_vencimiento.strftime('%d/%m/%Y')}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Tabla de cuotas
    story.append(Paragraph("CRONOGRAMA DE PAGOS", subtitle_style))
    
    # Obtener todas las cuotas ordenadas por fecha
    cuotas = prestamo.cuotas.all().order_by('fecha_pago')
    
    # Crear tabla
    data = [['N°', 'Fecha de Pago', 'Monto', 'Estado']]
    
    for i, cuota in enumerate(cuotas, 1):
        estado = "Pagado" if cuota.pagada else "Pendiente"
        data.append([
            str(i),
            cuota.fecha_pago.strftime('%d/%m/%Y'),
            f"${cuota.monto:,.2f}",
            estado
        ])
    
    # Crear la tabla
    table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Resumen
    total_cuotas = cuotas.count()
    cuotas_pagadas = cuotas.filter(pagada=True).count()
    cuotas_pendientes = total_cuotas - cuotas_pagadas
    monto_pagado = sum(cuota.monto for cuota in cuotas.filter(pagada=True))
    monto_pendiente = sum(cuota.monto for cuota in cuotas.filter(pagada=False))
    
    story.append(Paragraph("RESUMEN", subtitle_style))
    story.append(Paragraph(f"<b>Total de Cuotas:</b> {total_cuotas}", styles['Normal']))
    story.append(Paragraph(f"<b>Cuotas Pagadas:</b> {cuotas_pagadas}", styles['Normal']))
    story.append(Paragraph(f"<b>Cuotas Pendientes:</b> {cuotas_pendientes}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Pagado:</b> ${monto_pagado:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Pendiente:</b> ${monto_pendiente:,.2f}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Notas importantes
    story.append(Paragraph("NOTAS IMPORTANTES", subtitle_style))
    story.append(Paragraph("• Este calendario muestra las fechas de vencimiento de cada cuota.", styles['Normal']))
    story.append(Paragraph("• Es importante realizar los pagos en las fechas indicadas.", styles['Normal']))
    story.append(Paragraph("• En caso de retraso, pueden aplicarse intereses adicionales.", styles['Normal']))
    story.append(Paragraph("• Para cualquier consulta, contacte con nosotros.", styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    
    # Preparar la respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="calendario_pagos_{prestamo.cliente.nombre}_{prestamo.fecha_prestamo.strftime("%Y%m%d")}.pdf"'
    
    return response
    