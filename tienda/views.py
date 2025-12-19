from django.shortcuts import render, get_object_or_404, redirect 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
import uuid
import json
import time
from .flow_service import FlowService
from .models import Orden, Producto




# views.py - Versión PRÁCTICA para tu gimnasio
from django.shortcuts import render
from django.http import JsonResponse
import uuid
import time

def iniciar_pago_gimnasio(request):
    """Vista SIMPLE para la tienda del gimnasio"""
    
    if request.method == 'POST':
        try:
            # Datos del formulario de tu tienda
            email = request.POST.get('email')
            total = request.POST.get('total', 0)
            carrito = request.POST.get('carrito', '[]')
            
            # Validar
            if not email or int(total) < 100:
                return JsonResponse({
                    'error': True,
                    'mensaje': 'Email inválido o monto muy bajo'
                }, status=400)
            
            # Crear ID único para la orden
            orden_id = f"GIM-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            # Usar FlowService SIMPLIFICADO
            flow = FlowService()
            
            # Construir URLs absolutas
            dominio = request.build_absolute_uri('/').rstrip('/')
            
            datos_pago = {
                'commerceOrder': orden_id,
                'subject': f'Membresía/Productos Gimnasio Leblon - {orden_id}',
                'amount': int(total),
                'email': email,
                'urlConfirmation': f'{dominio}/webhook/flow/confirmar/',  # Webhook
                'urlReturn': f'{dominio}/tienda/gracias/?orden={orden_id}',  # Página de gracias
            }
            
            # Llamar a Flow
            resultado = flow.crear_pago(datos_pago)
            
            # Manejar respuesta
            if 'error' in resultado and resultado['error']:
                return JsonResponse({
                    'error': True,
                    'mensaje': 'No pudimos conectar con Flow',
                    'orden_id': orden_id
                }, status=400)
            
            # ¡ÉXITO! Redirigir a Flow
            return JsonResponse({
                'success': True,
                'url_pago': resultado.get('url'),
                'token': resultado.get('token'),
                'orden_id': orden_id
            })
            
        except Exception as e:
            return JsonResponse({
                'error': True,
                'mensaje': f'Error: {str(e)}'
            }, status=500)
    
    # GET: Mostrar página de pago
    return render(request, 'tienda/pago.html')

def webhook_confirmacion(request):
    """Webhook SIMPLE que recibe Flow"""
    token = request.GET.get('token') or request.POST.get('token')
    
    if token:
        # Aquí actualizas tu base de datos
        # Ej: Orden.objects.filter(flow_token=token).update(estado='pagado')
        print(f"✅ Webhook recibido! Token: {token}")
        
    return JsonResponse({'status': 'ok'})
# ==============================================
# 3. VISTAS DE TIENDA (sin cambios mayores)
# ==============================================

def formatear_precio(precio):
    """Formatea precio al estilo chileno: 27900 -> $27.900"""
    try:
        return f"${int(precio):,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${precio}"


def tienda(request):
    """Vista principal de la tienda"""
    productos = Producto.objects.filter(activo=True)
    for producto in productos:
        producto.precio_formateado = formatear_precio(producto.precio)
    return render(request, 'tienda.html', {'productos': productos})


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
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


# ==============================================
# 4. VISTA DE PRUEBA (solo desarrollo)
# ==============================================

@csrf_exempt
def prueba_flow_directa(request):
    """Vista de prueba directa - SOLO PARA DESARROLLO"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Solo disponible en modo desarrollo'}, status=403)
    
    if request.method == 'POST':
        try:
            # Usar sandbox en desarrollo
            flow_service = FlowServiceFixed(sandbox=True)
            
            # Datos de prueba mínimos
            order_data = {
                'commerceOrder': f"TEST-{int(time.time())}",
                'subject': 'Prueba de integración Flow',
                'amount': 1000,  # $1.000 CLP
                'email': 'test@example.com',
                'urlConfirmation': 'https://httpbin.org/post',  # Servicio de prueba
                'urlReturn': 'https://google.com',
            }
            
            result = flow_service.create_payment(order_data)
            
            return JsonResponse({
                'test_data': order_data,
                'flow_response': result,
                'sandbox': True
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=500)
    
    return JsonResponse({
        'message': 'POST con datos de prueba a este endpoint',
        'ejemplo_curl': '''
curl -X POST http://localhost:8000/prueba-flow/ -H "Content-Type: application/json"
'''
    })