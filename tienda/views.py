from django.shortcuts import render, get_object_or_404
from django.template import context
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
import uuid
import json

from .models import Orden, Producto
from .flow_service import FlowService




@csrf_exempt
def return_view(request):
    token = request.GET.get('token')
    status = request.GET.get('status')  # opcional, Flow a veces lo envía
    
    context = {
        'token': token,
        'status': status,
    }
    return render(request, 'tienda/return.html', context)  # crea esta plantilla




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

def iniciar_pago(request, producto_id):  # ← parámetro posicional, sin default
    # Obtener el producto de forma segura
    producto = get_object_or_404(Producto, id=producto_id)

    # Datos para Flow (usa valores reales del producto)
    order_data = {
        "commerceOrder": f"ORD-{producto_id}-{request.user.id if request.user.is_authenticated else 'anon'}",
        "subject": f"Compra: {producto.nombre}",
        "amount": int(producto.precio.replace('.', '') if isinstance(producto.precio, str) else producto.precio),
        "email": request.user.email if request.user.is_authenticated else "pergadetonao14@gmail.com",
        "urlConfirmation": "https://gimnasiolebloncalama.cl/confirm/",
        "urlReturn": "https://gimnasiolebloncalama.cl/tienda/return/"
    }

    # Crear instancia de Flow (sandbox para pruebas)
    flow = FlowService(environment="sandbox")  # Cambia a "prod" cuando estés listo

    result = flow.create_payment(order_data)

    if result and 'url' in result and 'token' in result:
        redirect_url = f"{result['url']}?token={result['token']}"
        return redirect(redirect_url)
    else:
        # Si falla, muestra error (puedes crear una plantilla)
        from django.http import HttpResponse
        return HttpResponse("Error al conectar con Flow. Intenta nuevamente.", status=500)


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
