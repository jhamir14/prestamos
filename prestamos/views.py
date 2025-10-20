from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import PrestamoForm, ClienteForm
from .models import Prestamo, Cliente, CuotaPago
from django.db import models
from django.db.models import Sum
from datetime import datetime, timedelta, date
import calendar
import logging
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from django.urls import reverse
from django.views.decorators.cache import cache_page, never_cache

# Configurar logger
logger = logging.getLogger(__name__)
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

@cache_page(20)
def index(request):
    # Solo usuarios autenticados pueden ver el panel
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Obtener parámetro de búsqueda
    search_query = request.GET.get('search', '')
    
    qs = Prestamo.objects.select_related('cliente')
    if search_query:
        prestamos = qs.filter(cliente__nombre__icontains=search_query)
    else:
        prestamos = qs.all()

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
                messages.success(request, f'Préstamo de S/ {prestamo.monto} creado exitosamente para {prestamo.cliente.nombre}. Se han generado las cuotas automáticamente.')
                return redirect('index')
            except Exception as e:
                logger.error(f"Error al crear préstamo: {e}")
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

def editar_prestamo(request, prestamo_id):
    # Solo usuarios autenticados pueden editar préstamos
    if not request.user.is_authenticated:
        return redirect('signin')
    
    try:
        prestamo = Prestamo.objects.get(id=prestamo_id)
    except Prestamo.DoesNotExist:
        messages.error(request, 'Préstamo no encontrado.')
        return redirect('index')
    
    if request.method == 'GET':
        form = PrestamoForm(instance=prestamo)
        action_url = reverse('editar_prestamo', args=[prestamo_id])
        return render(request, 'registrar_prestamo.html', {
            'form': form,
            'is_edit': True,
            'action_url': action_url
        })
    else:
        form = PrestamoForm(request.POST, instance=prestamo)
        if form.is_valid():
            try:
                prestamo = form.save()
                # Actualizar el monto de las cuotas pendientes según el nuevo monto del préstamo
                try:
                    nuevo_monto_por_cuota = prestamo.monto_por_cuota
                    prestamo.cuotas.filter(pagada=False).update(monto=nuevo_monto_por_cuota)
                except Exception as e_update:
                    logger.error(f"Error al actualizar montos de cuotas: {e_update}")
                    messages.warning(request, 'El préstamo se actualizó, pero hubo un problema al actualizar el monto de algunas cuotas.')
                else:
                    messages.success(request, f'Préstamo actualizado y montos de cuotas pendientes sincronizados para {prestamo.cliente.nombre}.')
                return redirect('calendario_pagos', prestamo_id=prestamo.id)
            except Exception as e:
                logger.error(f"Error al actualizar préstamo: {e}")
                return render(request, 'registrar_prestamo.html', {
                    'form': form,
                    'is_edit': True,
                    'action_url': reverse('editar_prestamo', args=[prestamo_id]),
                    'error': 'Error al actualizar el préstamo. Inténtalo de nuevo.'
                })
        else:
            return render(request, 'registrar_prestamo.html', {
                'form': form,
                'is_edit': True,
                'action_url': reverse('editar_prestamo', args=[prestamo_id]),
                'error': 'Por favor, corrige los errores en el formulario.'
            })

def calendario_pagos(request, prestamo_id):
    # Solo usuarios autenticados pueden ver el calendario
    if not request.user.is_authenticated:
        return redirect('signin')
    
    try:
        prestamo = Prestamo.objects.select_related('cliente').get(id=prestamo_id)
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
    
    # Obtener cuotas del préstamo para el mes/año seleccionados
    cuotas = (
        prestamo.cuotas
        .filter(fecha_pago__year=year, fecha_pago__month=month)
        .select_related('prestamo')
        .only('id', 'prestamo_id', 'fecha_pago', 'monto', 'pagada', 'fecha_pagada', 'tipo_cuota')
        .order_by('fecha_pago')
    )

    # Mapear cuotas por día para evitar bucles anidados en plantilla
    cuotas_por_dia = {}
    for cuota in cuotas:
        d = cuota.fecha_pago.day
        cuotas_por_dia.setdefault(d, []).append(cuota)
    
    context = {
        'prestamo': prestamo,
        'calendar': cal,
        'month_name': month_name,
        'month': month,
        'year': year,
        'cuotas': cuotas,
        'cuotas_por_dia': cuotas_por_dia,
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

    # Resolver de forma segura el préstamo asociado para redirección
    prestamo_id = (
        CuotaPago.objects
        .filter(id=cuota_id)
        .values_list('prestamo_id', flat=True)
        .first()
    )

    if request.method == 'POST' and prestamo_id:
        try:
            cuota = CuotaPago.objects.get(id=cuota_id)
            if cuota.prestamo.estado:
                messages.error(request, 'El préstamo está cancelado.')
            else:
                if not cuota.pagada:
                    cuota.pagada = True
                    cuota.fecha_pagada = datetime.now().date()
                    cuota.save(update_fields=['pagada', 'fecha_pagada'])
                messages.success(request, f'Cuota de S/{cuota.monto} marcada como pagada.')
        except CuotaPago.DoesNotExist:
            messages.error(request, 'Cuota no encontrada.')

    # Redirigir de vuelta al calendario o al índice si no existe
    if prestamo_id:
        return redirect('calendario_pagos', prestamo_id=prestamo_id)
    return redirect('index')


def desmarcar_cuota_pagada(request, cuota_id):
    """Desmarca una cuota como pagada"""
    if not request.user.is_authenticated:
        return redirect('signin')

    # Resolver de forma segura el préstamo asociado para redirección
    prestamo_id = (
        CuotaPago.objects
        .filter(id=cuota_id)
        .values_list('prestamo_id', flat=True)
        .first()
    )

    if request.method == 'POST' and prestamo_id:
        try:
            cuota = CuotaPago.objects.get(id=cuota_id)
            if cuota.prestamo.estado:
                messages.error(request, 'El préstamo está cancelado.')
            else:
                if cuota.pagada:
                    cuota.pagada = False
                    cuota.fecha_pagada = None
                    cuota.save(update_fields=['pagada', 'fecha_pagada'])
                messages.success(request, f'Cuota de S/{cuota.monto} desmarcada como pagada.')
        except CuotaPago.DoesNotExist:
            messages.error(request, 'Cuota no encontrada.')

    # Redirigir de vuelta al calendario o al índice si no existe
    if prestamo_id:
        return redirect('calendario_pagos', prestamo_id=prestamo_id)
    return redirect('index')

def signout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

def prestamos_diarios(request):
    """Vista para mostrar solo préstamos diarios"""
    # Solo usuarios autenticados pueden ver los préstamos
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Obtener parámetro de búsqueda
    search_query = request.GET.get('search', '')
    
    qs = Prestamo.objects.select_related('cliente').filter(forma_pago='diario')
    if search_query:
        prestamos = qs.filter(cliente__nombre__icontains=search_query)
    else:
        prestamos = qs

    # Calcular el total de dinero prestado con agregación
    total_prestado = prestamos.aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'prestamos_diarios.html', {
        'prestamos': prestamos,
        'search_query': search_query,
        'tipo_prestamo': 'diario',
        'total_prestado': total_prestado
    })

def prestamos_semanales(request):
    """Vista para mostrar solo préstamos semanales"""
    # Solo usuarios autenticados pueden ver los préstamos
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Obtener parámetro de búsqueda
    search_query = request.GET.get('search', '')
    
    qs = Prestamo.objects.select_related('cliente').filter(forma_pago='semanal')
    if search_query:
        prestamos = qs.filter(cliente__nombre__icontains=search_query)
    else:
        prestamos = qs

    # Calcular el total de dinero prestado con agregación
    total_prestado = prestamos.aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'prestamos_semanales.html', {
        'prestamos': prestamos,
        'search_query': search_query,
        'tipo_prestamo': 'semanal',
        'total_prestado': total_prestado
    })

@never_cache
def reporte_pagos(request):
    """Muestra un reporte de pagos que vencen hoy y préstamos con cuotas retrasadas"""
    # Solo usuarios autenticados pueden ver el reporte
    if not request.user.is_authenticated:
        return redirect('signin')
    
    try:
        # Obtener la fecha actual
        hoy = date.today()
        # Consultas optimizadas con select_related y campos necesarios
        cuotas_vencidas_hoy = (
            CuotaPago.objects
            .filter(fecha_pago=hoy, pagada=False)
            .select_related('prestamo__cliente')
            .order_by('prestamo__cliente__nombre')
        )
        cuotas_retrasadas = (
            CuotaPago.objects
            .filter(fecha_pago__lt=hoy, pagada=False)
            .select_related('prestamo__cliente')
            .order_by('prestamo__cliente__nombre', 'fecha_pago')
        )
        # Calcular totales usando agregaciones
        total_cuotas_hoy = cuotas_vencidas_hoy.count()
        total_monto_hoy = cuotas_vencidas_hoy.aggregate(total=Sum('monto'))['total'] or 0
        total_cuotas_retrasadas = cuotas_retrasadas.count()
        total_monto_retrasadas = cuotas_retrasadas.aggregate(total=Sum('monto'))['total'] or 0
        prestamos_activos = Prestamo.objects.filter(estado=False).count()
        prestamos_diarios_activos = Prestamo.objects.filter(forma_pago='diario', estado=False).count()
        prestamos_semanales_activos = Prestamo.objects.filter(forma_pago='semanal', estado=False).count()
        cuotas_pagadas_hoy = CuotaPago.objects.filter(fecha_pago=hoy, pagada=True).count()
        context = {
            'cuotas_vencidas_hoy': cuotas_vencidas_hoy,
            'cuotas_retrasadas': cuotas_retrasadas,
            'total_cuotas_hoy': total_cuotas_hoy,
            'total_monto_hoy': total_monto_hoy,
            'total_cuotas_retrasadas': total_cuotas_retrasadas,
            'total_monto_retrasadas': total_monto_retrasadas,
            'prestamos_activos': prestamos_activos,
            'prestamos_diarios_activos': prestamos_diarios_activos,
            'prestamos_semanales_activos': prestamos_semanales_activos,
            'cuotas_pagadas_hoy': cuotas_pagadas_hoy,
            'fecha_hoy': hoy,
        }
        return render(request, 'reporte_pagos.html', context)
    except Exception as e:
        logger.error(f"Error general en reporte_pagos: {e}")
        messages.error(request, 'Hubo un error al cargar el reporte. Por favor, inténtalo de nuevo.')
        return redirect('index')

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
    story.append(Paragraph(f"<b>Monto del Préstamo:</b> S/ {prestamo.monto:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Total a Pagar:</b> S/ {prestamo.monto_total:,.2f}", styles['Normal']))
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
        if cuota.pagada:
            estado = "Pagado"
        elif prestamo.estado:  # Si el préstamo está cancelado
            estado = "Cancelado"
        else:
            estado = "Pendiente"
        data.append([
            str(i),
            cuota.fecha_pago.strftime('%d/%m/%Y'),
            f"S/ {cuota.monto:,.2f}",
            estado
        ])
    
    # Crear la tabla
    table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch])
    
    # Crear estilos de tabla
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]
    
    # Aplicar colores según el estado de cada fila
    for i, row in enumerate(data[1:], 1):  # Saltar el encabezado
        estado = row[3]  # El estado está en la columna 3
        if estado == "Pagado":
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgreen))
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.darkgreen))
        elif estado == "Cancelado":
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightcoral))
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.darkred))
        else:  # Pendiente
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightyellow))
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.darkorange))
    
    table.setStyle(TableStyle(table_style))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Resumen
    total_cuotas = cuotas.count()
    cuotas_pagadas = cuotas.filter(pagada=True).count()
    cuotas_pendientes = total_cuotas - cuotas_pagadas
    monto_pagado = cuotas.filter(pagada=True).aggregate(total=Sum('monto'))['total'] or 0
    monto_pendiente = cuotas.filter(pagada=False).aggregate(total=Sum('monto'))['total'] or 0
    
    story.append(Paragraph("RESUMEN", subtitle_style))
    story.append(Paragraph(f"<b>Total de Cuotas:</b> {total_cuotas}", styles['Normal']))
    story.append(Paragraph(f"<b>Cuotas Pagadas:</b> {cuotas_pagadas}", styles['Normal']))
    story.append(Paragraph(f"<b>Cuotas Pendientes:</b> {cuotas_pendientes}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Pagado:</b> S/ {monto_pagado:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Monto Pendiente:</b> S/ {monto_pendiente:,.2f}", styles['Normal']))
    
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

@csrf_exempt
@require_http_methods(["GET"])
def buscar_clientes(request):
    """API endpoint para buscar clientes con autocompletado"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'clientes': []})
        
        # Buscar clientes que coincidan con el nombre o email
        clientes = Cliente.objects.filter(
            models.Q(nombre__icontains=query) | 
            models.Q(email__icontains=query) |
            models.Q(telefono__icontains=query)
        )[:10]  # Limitar a 10 resultados
        
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'direccion': cliente.direccion,
                'ciudad': cliente.ciudad,
                'pais': cliente.pais,
                'texto_completo': f"{cliente.nombre} - {cliente.email} - {cliente.telefono}"
            })
        
        return JsonResponse({'clientes': resultados})
        
    except Exception as e:
        logger.error(f"Error en búsqueda de clientes: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    