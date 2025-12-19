from django.shortcuts import render, get_object_or_404, redirect 
from .models import Producto
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
import uuid
from .flow_service import FlowService
from .models import Orden



def iniciar_pago(request):
    """Vista para iniciar el proceso de pago"""
    if request.method == 'POST':
        # Obtener datos del carrito (debes ajustar según tu implementación)
        email = request.POST.get('email')
        total = int(request.POST.get('total'))
        productos = request.POST.get('productos')  # JSON string
        
        # Generar ID único para la orden
        orden_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear orden en la base de datos
        orden = Orden.objects.create(
            orden_id=orden_id,
            email=email,
            total=total,
            productos=productos,
            estado='pendiente'
        )
        
        # Preparar datos para Flow
        flow_service = FlowService()
        order_data = {
            'commerceOrder': orden_id,
            'subject': f'Compra en Gimnasio Leblon - {orden_id}',
            'amount': total,
            'email': email,
            'urlConfirmation': request.build_absolute_uri(reverse('confirmar_pago')),
            'urlReturn': request.build_absolute_uri(reverse('resultado_pago')),
        }
        
        # Crear pago en Flow
        result = flow_service.create_payment(order_data)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        # Guardar token de Flow
        orden.flow_token = result.get('token')
        orden.flow_order = result.get('flowOrder')
        orden.save()
        
        # Redirigir a Flow
        return redirect(f"{result['url']}?token={result['token']}")
    
    return render(request, 'checkout.html')

@csrf_exempt
def confirmar_pago(request):
    """Webhook para confirmar el pago (llamado por Flow)"""
    if request.method == 'POST':
        token = request.POST.get('token')
        
        flow_service = FlowService()
        payment_status = flow_service.get_payment_status(token)
        
        if 'error' not in payment_status:
            try:
                orden = Orden.objects.get(flow_token=token)
                
                # Actualizar estado según respuesta de Flow
                if payment_status.get('status') == 2:  # 2 = Pagado
                    orden.estado = 'pagado'
                else:
                    orden.estado = 'fallido'
                
                orden.save()
                
                return JsonResponse({'status': 'ok'})
            except Orden.DoesNotExist:
                return JsonResponse({'error': 'Orden no encontrada'}, status=404)
        
        return JsonResponse({'error': 'Error al verificar pago'}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def resultado_pago(request):
    """Página de resultado después del pago"""
    token = request.GET.get('token')
    
    try:
        orden = Orden.objects.get(flow_token=token)
        
        flow_service = FlowService()
        payment_status = flow_service.get_payment_status(token)
        
        context = {
            'orden': orden,
            'payment_status': payment_status,
            'exitoso': orden.estado == 'pagado'
        }
        
        return render(request, 'resultado_pago.html', context)
    except Orden.DoesNotExist:
        return render(request, 'resultado_pago.html', {
            'error': 'Orden no encontrada'
        })

def formatear_precio(precio):
    """Formatea precio al estilo chileno: 27900 -> $27.900"""
    try:
        return f"${int(precio):,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${precio}"

def tienda(request):
    """Vista principal de la tienda"""
    productos = Producto.objects.all()
    for producto in productos:
        producto.precio_formateado = formatear_precio(producto.precio)
    return render(request, 'tienda.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.precio_formateado = formatear_precio(producto.precio)
    
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto_id)[:3]
    
    for prod in productos_relacionados:
        prod.precio_formateado = formatear_precio(prod.precio)

    return render(request, 'detalle_producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })