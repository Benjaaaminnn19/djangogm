from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import uuid
import json
import time

from .flow_service import FlowService
from .models import Orden, Producto


# ==============================================
# UTILIDADES
# ==============================================

def formatear_precio(precio):
    """Formatea precio al estilo chileno: 27900 -> $27.900"""
    try:
        return f"${int(precio):,}".replace(",", ".")
    except (ValueError, TypeError):
        return f"${precio}"


# ==============================================
# PAGO FLOW
# ==============================================

def iniciar_pago(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip()
            total = request.POST.get("total", "0")
            productos_json = request.POST.get("productos", "[]")

            if not email or "@" not in email:
                return JsonResponse({"error": True, "message": "Email inválido"}, status=400)

            try:
                total_int = int(total)
                if total_int <= 0:
                    raise ValueError
            except ValueError:
                return JsonResponse({"error": True, "message": "Monto inválido"}, status=400)

            orden_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            orden = Orden.objects.create(
                orden_id=orden_id,
                email=email,
                total=total_int,
                productos=productos_json,
                estado="pendiente"
            )

            usar_sandbox = getattr(settings, "FLOW_SANDBOX", settings.DEBUG)
            flow_service = FlowService(sandbox=usar_sandbox)

            base_url = request.build_absolute_uri("/").rstrip("/")

            order_data = {
                "commerceOrder": orden_id,
                "subject": f"Compra en Gimnasio Leblon - {orden_id}",
                "amount": total_int,
                "email": email,
                "urlConfirmation": f"{base_url}{reverse('confirmar_pago')}",
                "urlReturn": f"{base_url}{reverse('resultado_pago')}",
            }

            result = flow_service.create_payment(order_data)

            if result.get("error"):
                orden.estado = "error_flow"
                orden.save()

                return JsonResponse({
                    "error": True,
                    "message": "Error al crear pago en Flow",
                    "flow_error_code": result.get("code"),
                    "flow_error_message": result.get("message"),
                    "orden_id": orden_id
                }, status=400)

            orden.flow_token = result.get("token")
            orden.flow_order = result.get("flowOrder")
            orden.save()

            return JsonResponse({
                "success": True,
                "url": result.get("url"),
                "token": result.get("token"),
                "orden_id": orden_id
            })

        except Exception as e:
            return JsonResponse({"error": True, "message": str(e)}, status=500)

    productos = Producto.objects.filter(activo=True)
    productos_data = [{
        "id": p.id,
        "nombre": p.nombre,
        "precio": p.precio,
        "precio_formateado": formatear_precio(p.precio),
        "imagen": p.imagen.url if p.imagen else ""
    } for p in productos]

    return render(request, "checkout.html", {
        "productos_json": json.dumps(productos_data),
        "DEBUG": settings.DEBUG
    })


@csrf_exempt
def confirmar_pago(request):
    data = request.GET if request.method == "GET" else request.POST
    token = data.get("token")

    if not token:
        return JsonResponse({"error": True, "message": "Token no proporcionado"}, status=400)

    try:
        orden = Orden.objects.get(flow_token=token)

        usar_sandbox = getattr(settings, "FLOW_SANDBOX", settings.DEBUG)
        flow_service = FlowService(sandbox=usar_sandbox)

        payment_status = flow_service.get_payment_status(token)

        status_code = payment_status.get("status")

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


def resultado_pago(request):
    token = request.GET.get("token")

    if not token:
        return render(request, "resultado_pago.html", {
            "error": True,
            "mensaje": "Token no recibido"
        })

    try:
        orden = Orden.objects.get(flow_token=token)

        context = {
            "orden": orden,
            "exitoso": orden.estado == "pagado",
            "fallido": orden.estado in ["rechazado", "anulado", "error_flow"],
            "pendiente": orden.estado == "pendiente",
            "total_formateado": formatear_precio(orden.total),
            "productos": json.loads(orden.productos)
        }

        return render(request, "resultado_pago.html", context)

    except Orden.DoesNotExist:
        return render(request, "resultado_pago.html", {
            "error": True,
            "mensaje": "Orden no encontrada"
        })


# ==============================================
# TIENDA
# ==============================================

def tienda(request):
    productos = Producto.objects.filter(activo=True)
    for p in productos:
        p.precio_formateado = formatear_precio(p.precio)
    return render(request, "tienda.html", {"productos": productos})


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    producto.precio_formateado = formatear_precio(producto.precio)

    relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto_id)[:3]

    for p in relacionados:
        p.precio_formateado = formatear_precio(p.precio)

    return render(request, "detalle_producto.html", {
        "producto": producto,
        "productos_relacionados": relacionados
    })
