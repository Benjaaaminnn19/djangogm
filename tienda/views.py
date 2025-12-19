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


# ==============================================
# 1. SERVICIO FLOW ACTUALIZADO (incluido aquí por si acaso)
# ==============================================
import hmac
import hashlib
import requests
import urllib.parse

class FlowServiceFixed:
    """Servicio Flow CORREGIDO - Incluido aquí temporalmente"""
    
    def __init__(self, sandbox=False):
        self.sandbox = sandbox
        
        # Obtener credenciales de settings
        self.api_key = getattr(settings, 'FLOW_API_KEY', '').strip()
        self.secret_key = getattr(settings, 'FLOW_SECRET_KEY', '').strip()
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales de Flow no configuradas en settings")
        
        print(f"[FLOW] API Key: {self.api_key[:8]}...")
        print(f"[FLOW] Ambiente: {'SANDBOX' if sandbox else 'PRODUCCIÓN'}")
    
    @property
    def base_url(self):
        return "https://sandbox.flow.cl/api" if self.sandbox else "https://www.flow.cl/api"
    
    def _generate_signature(self, params):
    # Excluir 's'
        params_to_sign = {k: v for k, v in params.items() if k != 's'}

    # Ordenar alfabéticamente
        sorted_params = sorted(params_to_sign.items())

    # Crear string base SIN URL ENCODE
        base_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        base_string += f"&secretKey={self.secret_key}"

    # SHA256 plano
        signature = hashlib.sha256(
            base_string.encode("utf-8")
        ).hexdigest()

        return signature

    
    def create_payment(self, order_data):
        """Crea pago en Flow - VERSIÓN CORREGIDA"""
        # Validar campos requeridos
        required = ['commerceOrder', 'subject', 'amount', 'email', 
                   'urlConfirmation', 'urlReturn']
        for field in required:
            if field not in order_data:
                return {'error': True, 'message': f'Falta campo: {field}'}
        
        # Timestamp
        timestamp = str(int(time.time()))
        
        # Parámetros
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(order_data['commerceOrder']),
            'subject': str(order_data['subject']),
            'currency': 'CLP',
            'amount': str(order_data['amount']),
            'email': str(order_data['email']),
            'urlConfirmation': str(order_data['urlConfirmation']),
            'urlReturn': str(order_data['urlReturn']),
            'timestamp': timestamp
        }
        
        # Opcionales
        if 'optional' in order_data and order_data['optional']:
            params['optional'] = str(order_data['optional'])
        
        # Generar firma
        params['s'] = self._generate_signature(params)
        
        # Construir URL
        url_parts = []
        for key, value in params.items():
            if key == 's':
                url_parts.append(f"{key}={value}")
            else:
                encoded_value = urllib.parse.quote_plus(str(value))
                url_parts.append(f"{key}={encoded_value}")
        
        query_string = '&'.join(url_parts)
        url = f"{self.base_url}/payment/create?{query_string}"
        
        # DEBUG
        if settings.DEBUG:
            print(f"[FLOW DEBUG] URL: {url[:200]}...")
        
        # Enviar petición GET
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_data = response.json()
                    return {'error': True, 'data': error_data}
                except:
                    return {'error': True, 'message': response.text}
                    
        except Exception as e:
            return {'error': True, 'message': str(e)}
    
    def get_payment_status(self, token):
        """Obtiene estado de pago"""
        timestamp = str(int(time.time()))
        
        params = {
            'apiKey': self.api_key,
            'token': token,
            'timestamp': timestamp
        }
        
        params['s'] = self._generate_signature(params)
        
        # Construir URL
        url_parts = []
        for key, value in params.items():
            if key == 's':
                url_parts.append(f"{key}={value}")
            else:
                encoded_value = urllib.parse.quote_plus(str(value))
                url_parts.append(f"{key}={encoded_value}")
        
        query_string = '&'.join(url_parts)
        url = f"{self.base_url}/payment/getStatus?{query_string}"
        
        try:
            response = requests.get(url, timeout=30)
            return response.json()
        except Exception as e:
            return {'error': True, 'message': str(e)}


# ==============================================
# 2. VISTAS CORREGIDAS
# ==============================================

def iniciar_pago(request):
    """Vista para iniciar el proceso de pago - CORREGIDA"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.POST.get('email', '').strip()
            total = request.POST.get('total', '0')
            productos_json = request.POST.get('productos', '[]')
            
            # Validaciones básicas
            if not email or '@' not in email:
                return JsonResponse({
                    'error': True,
                    'message': 'Email inválido'
                }, status=400)
            
            try:
                total_int = int(total)
                if total_int <= 0:
                    return JsonResponse({
                        'error': True,
                        'message': 'Monto inválido'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'error': True,
                    'message': 'Monto inválido'
                }, status=400)
            
            # Generar ID único para la orden
            orden_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Crear orden en la base de datos
            orden = Orden.objects.create(
                orden_id=orden_id,
                email=email,
                total=total_int,
                productos=productos_json,
                estado='pendiente'
            )
            
            # Determinar si usar sandbox (solo en desarrollo)
            usar_sandbox = getattr(settings, 'FLOW_SANDBOX', settings.DEBUG)
            
            # Preparar datos para Flow
            flow_service = FlowServiceFixed(sandbox=usar_sandbox)
            
            # Construir URLs absolutas
            base_url = request.build_absolute_uri('/').rstrip('/')
            
            order_data = {
                'commerceOrder': orden_id,
                'subject': f'Compra en Gimnasio Leblon - {orden_id}',
                'amount': total_int,
                'email': email,
                'urlConfirmation': f"{base_url}{reverse('confirmar_pago')}",
                'urlReturn': f"{base_url}{reverse('resultado_pago')}",
                'optional': f"Orden: {orden_id}"
            }
            
            # Crear pago en Flow
            result = flow_service.create_payment(order_data)
            
            # DEBUG
            if settings.DEBUG:
                print(f"[DEBUG] Resultado Flow: {result}")
            
            # Verificar resultado
            if 'error' in result and result.get('error'):
                # Actualizar orden como fallida
                orden.estado = 'error_flow'
                orden.save()
                
                # Devolver error detallado
                error_detail = result.get('data', {})
                return JsonResponse({
                    'error': True,
                    'message': 'Error al crear pago en Flow',
                    'flow_error_code': error_detail.get('code'),
                    'flow_error_message': error_detail.get('message'),
                    'orden_id': orden_id
                }, status=400)
            
            # Guardar token de Flow
            orden.flow_token = result.get('token')
            orden.flow_order = result.get('flowOrder')
            orden.save()
            
            # Éxito - devolver URL para redirección
            return JsonResponse({
                'success': True,
                'url': result.get('url'),
                'token': result.get('token'),
                'orden_id': orden_id
            })
            
        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    # GET request - mostrar formulario
    productos = Producto.objects.filter(activo=True)
    productos_data = []
    for p in productos:
        productos_data.append({
            'id': p.id,
            'nombre': p.nombre,
            'precio': p.precio,
            'precio_formateado': formatear_precio(p.precio),
            'imagen': p.imagen.url if p.imagen else ''
        })
    
    return render(request, 'checkout.html', {
        'productos_json': json.dumps(productos_data),
        'DEBUG': settings.DEBUG
    })


@csrf_exempt
def confirmar_pago(request):
    """Webhook para confirmar el pago (llamado por Flow) - CORREGIDA"""
    if request.method == 'GET' or request.method == 'POST':
        # Flow puede enviar por GET o POST
        data = request.GET if request.method == 'GET' else request.POST
        token = data.get('token')
        
        if not token:
            return JsonResponse({
                'error': True,
                'message': 'Token no proporcionado'
            }, status=400)
        
        try:
            # Buscar orden
            orden = Orden.objects.get(flow_token=token)
            
            # Usar el mismo ambiente que al crear el pago
            usar_sandbox = getattr(settings, 'FLOW_SANDBOX', settings.DEBUG)
            flow_service = FlowServiceFixed(sandbox=usar_sandbox)
            
            # Obtener estado del pago
            payment_status = flow_service.get_payment_status(token)
            
            if 'error' in payment_status and payment_status.get('error'):
                # Error al verificar
                orden.estado = 'error_verificacion'
                orden.save()
                return JsonResponse({
                    'error': True,
                    'message': 'Error al verificar pago'
                }, status=400)
            
            # Actualizar orden según estado de Flow
            # Códigos de Flow: 1=Pendiente, 2=Pagado, 3=Rechazado, 4=Anulado
            status_code = payment_status.get('status')
            
            if status_code == 2:  # Pagado
                orden.estado = 'pagado'
                orden.pagado = True
                mensaje = 'Pago confirmado exitosamente'
            elif status_code == 3:  # Rechazado
                orden.estado = 'rechazado'
                mensaje = 'Pago rechazado'
            elif status_code == 4:  # Anulado
                orden.estado = 'anulado'
                mensaje = 'Pago anulado'
            else:  # 1 = Pendiente u otros
                orden.estado = 'pendiente'
                mensaje = 'Pago aún pendiente'
            
            orden.save()
            
            # Responder a Flow
            return JsonResponse({
                'status': 'ok',
                'message': mensaje,
                'orden_id': orden.orden_id,
                'estado': orden.estado
            })
            
        except Orden.DoesNotExist:
            return JsonResponse({
                'error': True,
                'message': 'Orden no encontrada'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'error': True,
        'message': 'Método no permitido'
    }, status=405)


def resultado_pago(request):
    """Página de resultado después del pago - CORREGIDA"""
    token = request.GET.get('token')
    
    if not token:
        return render(request, 'resultado_pago.html', {
            'error': True,
            'mensaje': 'No se proporcionó token de pago'
        })
    
    try:
        orden = Orden.objects.get(flow_token=token)
        
        # Intentar obtener estado actualizado si aún está pendiente
        if orden.estado == 'pendiente':
            usar_sandbox = getattr(settings, 'FLOW_SANDBOX', settings.DEBUG)
            flow_service = FlowServiceFixed(sandbox=usar_sandbox)
            
            payment_status = flow_service.get_payment_status(token)
            if 'error' not in payment_status:
                status_code = payment_status.get('status')
                if status_code == 2:
                    orden.estado = 'pagado'
                    orden.pagado = True
                elif status_code == 3:
                    orden.estado = 'rechazado'
                elif status_code == 4:
                    orden.estado = 'anulado'
                orden.save()
        
        # Formatear productos para mostrar
        try:
            productos_data = json.loads(orden.productos)
        except:
            productos_data = []
        
        context = {
            'orden': orden,
            'productos': productos_data,
            'exitoso': orden.estado == 'pagado',
            'fallido': orden.estado in ['rechazado', 'anulado', 'error_flow', 'error_verificacion'],
            'pendiente': orden.estado == 'pendiente',
            'total_formateado': formatear_precio(orden.total)
        }
        
        return render(request, 'resultado_pago.html', context)
        
    except Orden.DoesNotExist:
        return render(request, 'resultado_pago.html', {
            'error': True,
            'mensaje': 'Orden no encontrada'
        })


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