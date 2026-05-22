from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required  # ← CAMBIO 1: Importación añadida
import uuid
import json
import logging
import time
from .models import Orden, Producto
from .flow_service import FlowService

logger = logging.getLogger(__name__)


@csrf_exempt
def return_view(request):
    token = request.POST.get('token') or request.GET.get('token')

    return render(request, 'return.html', {
        'token': token,
    })


# =====================================================
# UTILIDAD
# =====================================================

def formatear_precio(precio):
    """27900 -> $27.900"""
    try:
        return f"${int(precio):,}".replace(",", ".")
    except Exception:
        return f"${precio}"


# =====================================================
# OBTENER EMAIL DEL USUARIO  ← CAMBIO 2
# =====================================================

def obtener_email_usuario(request):
    """
    Devuelve el email del usuario autenticado.
    Lanza ValueError si no está logueado o no tiene email registrado,
    para que las vistas de pago puedan manejarlo explícitamente.
    """
    if not request.user.is_authenticated:
        raise ValueError("El usuario no ha iniciado sesión.")

    email = getattr(request.user, 'email', None)
    if not email or not email.strip():
        raise ValueError(
            f"El usuario '{request.user}' no tiene un correo electrónico registrado. "
            "Por favor, añade un correo desde tu perfil antes de realizar un pago."
        )

    return email.strip()


# =====================================================
# INICIAR PAGO  ← CAMBIO 3: @login_required añadido
# =====================================================

@login_required(login_url='/login/')
def iniciar_pago(request, producto_id):
    try:
        email = obtener_email_usuario(request)
    except ValueError as e:
        return render(request, 'tienda.html', {
            'productos': Producto.objects.filter(activo=True),
            'error_pago': str(e),
        })

    producto = get_object_or_404(Producto, id=producto_id)

    try:
        amount = int(float(producto.precio))
    except Exception as e:
        logger.error(f"Error procesando precio: {e}")
        return HttpResponse("Precio del producto inválido", status=400)

    commerce_order = f"ORD-{producto_id}-{int(time.time())}"
    flow = FlowService()

    result = flow.create_payment(
        commerce_order=commerce_order,
        subject=f"Compra: {producto.nombre}",
        amount=amount,
        email=email,
        url_confirmation="https://gimnasiolebloncalama.cl/confirm/",
        url_return="https://gimnasiolebloncalama.cl/tienda/return/",
    )

    if result and 'url' in result and 'token' in result:
        return redirect(f"{result['url']}?token={result['token']}")

    return HttpResponse("Error al conectar con Flow. Revisa los logs.", status=500)

# =====================================================
# CONFIRMACIÓN FLOW (WEBHOOK)
# =====================================================

@csrf_exempt
def confirmar_pago(request):
    data = request.GET if request.method == "GET" else request.POST
    token = data.get("token")

    if not token:
        return JsonResponse({"error": True, "message": "Token no recibido"}, status=400)

    try:
        orden = Orden.objects.get(flow_token=token)

        usar_sandbox = getattr(settings, "FLOW_SANDBOX", settings.DEBUG)
        flow_service = FlowService(sandbox=usar_sandbox)

        estado = flow_service.obtener_estado_pago(token)

        if "status" not in estado:
            orden.estado = "error_verificacion"
            orden.save()
            return JsonResponse({"error": True, "message": "Error al verificar pago"}, status=400)

        status_code = estado["status"]

        if status_code == 2:
            orden.estado = "pagado"
            orden.pagado = True
        elif status_code == 3:
            orden.estado = "rechazado"
        elif status_code == 4:
            orden.estado = "anulado"
        else:
            orden.estado = "pendiente"

        orden.save()

        return JsonResponse({"status": "ok"})

    except Orden.DoesNotExist:
        return JsonResponse({"error": True, "message": "Orden no encontrada"}, status=404)


# =====================================================
# RESULTADO DEL PAGO
# =====================================================

def resultado_pago(request):
    token = request.GET.get("token")

    if not token:
        return render(
            request,
            "resultado_pago.html",
            {"error": True, "mensaje": "Token no recibido"},
        )

    try:
        orden = Orden.objects.get(flow_token=token)

        try:
            productos = json.loads(orden.productos)
        except Exception:
            productos = []

        return render(
            request,
            "resultado_pago.html",
            {
                "orden": orden,
                "productos": productos,
                "exitoso": orden.estado == "pagado",
                "fallido": orden.estado in ["rechazado", "anulado", "error_flow"],
                "pendiente": orden.estado == "pendiente",
                "total_formateado": formatear_precio(orden.total),
            },
        )

    except Orden.DoesNotExist:
        return render(
            request,
            "resultado_pago.html",
            {"error": True, "mensaje": "Orden no encontrada"},
        )


# =====================================================
# TIENDA
# =====================================================

def tienda(request):
    productos = Producto.objects.filter(activo=True)
    for p in productos:
        p.precio_formateado = formatear_precio(p.precio)
    return render(request, "tienda.html", {"productos": productos})


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    producto.precio_formateado = formatear_precio(producto.precio)

    relacionados = (
        Producto.objects.filter(categoria=producto.categoria, activo=True)
        .exclude(id=producto_id)[:3]
    )

    for p in relacionados:
        p.precio_formateado = formatear_precio(p.precio)

    return render(
        request,
        "detalle_producto.html",
        {"producto": producto, "productos_relacionados": relacionados},
    )


# =====================================================
# PAGO MÚLTIPLE (CARRITO)  ← CAMBIO 3: @login_required añadido
# =====================================================

@login_required(login_url='/login/')
def pago_multiplo(request):
    # Obtener email dinámicamente; redirigir con mensaje si falta
    try:
        email = obtener_email_usuario(request)
    except ValueError as e:
        return render(request, 'tienda.html', {
            'productos': Producto.objects.filter(activo=True),
            'error_pago': str(e),
        })

    try:
        amount = int(request.GET.get('amount', 0))
        subject = request.GET.get('subject', 'Compra en Leblon Gym')
    except Exception:
        return HttpResponse("Error en los parámetros")

    if amount < 1000:
        return HttpResponse("Monto mínimo $1.000 CLP")

    commerce_order = f"ORD-MULTI-{int(time.time())}"

    flow = FlowService()

    result = flow.create_payment(
        commerce_order=commerce_order,
        subject=subject,
        amount=amount,
        email=email,  
        url_confirmation="https://gimnasiolebloncalama.cl/confirm/",
        url_return="https://gimnasiolebloncalama.cl/tienda/return/",
    )

    if result and 'url' in result and 'token' in result:
        return redirect(f"{result['url']}?token={result['token']}")

    return HttpResponse("Error al conectar con Flow", status=500)
