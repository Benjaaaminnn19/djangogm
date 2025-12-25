from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
import uuid
import json
import logging

from .models import Orden, Producto
from .flow_service import FlowService




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
# INICIAR PAGO
# =====================================================


logger = logging.getLogger(__name__)
def iniciar_pago(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    order_data = {
        "commerceOrder": f"ORD-{producto_id}-{request.user.id if request.user.is_authenticated else 'anon'}",
        "subject": f"Compra: {producto.nombre}",
        "amount": int(producto.precio.replace('.', '') if isinstance(producto.precio, str) else producto.precio),
        "email": request.user.email if request.user.is_authenticated else "pergadetonao14@gmail.com",
        "urlConfirmation": "https://gimnasiolebloncalama.cl/confirm/",
        "urlReturn": "https://gimnasiolebloncalama.cl/tienda/return/"
    }

    flow = FlowService(environment="sandbox")

    # === DEBUG: Esto es lo importante ===
    result = flow.create_payment(order_data)
    
    logger.info("FLOW RESULT: %s", result)  # Verás esto en los logs de Railway
    
    if result and 'url' in result and 'token' in result:
        redirect_url = f"{result['url']}?token={result['token']}"
        return redirect(redirect_url)
    else:
        # Mostramos más info para debug
        error_msg = "Error al conectar con Flow.<br><br>"
        if result is None:
            error_msg += "No se recibió respuesta (posible error de conexión o status != 200)."
        else:
            error_msg += f"Respuesta de Flow: {result}"
        
        return HttpResponse(error_msg, status=500)
  

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
