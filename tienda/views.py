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
                    raise ValueError()
            except ValueError:
                return JsonResponse({"error": True, "message": "Monto inválido"}, status=400)

            orden_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            orden = Orden.objects.create(
                orden_id=orden_id,
                email=email,
                total=total_int,
                productos=productos_json,
                estado="pendiente",
            )

            usar_sandbox = getattr(settings, "FLOW_SANDBOX", settings.DEBUG)
            flow_service = FlowService(sandbox=usar_sandbox)

            base_url = request.build_absolute_uri("/").rstrip("/")

            order_data = {
                "commerceOrder": orden_id,
                "subject": f"Compra Gimnasio Leblon - {orden_id}",
                "amount": total_int,
                "email": email,
                "urlConfirmation": f"{base_url}{reverse('confirmar_pago')}",
                "urlReturn": f"{base_url}{reverse('resultado_pago')}",
                "optional": f"Orden {orden_id}",
            }

            result = flow_service.crear_pago(order_data)


            # 🔴 VALIDACIÓN REAL DE FLOW
            if not result or "url" not in result or "token" not in result:
                orden.estado = "error_flow"
                orden.save()

                return JsonResponse(
                    {
                        "error": True,
                        "message": "Flow no creó el pago",
                        "flow_response": result,
                        "orden_id": orden_id,
                    },
                    status=400,
                )

            orden.flow_token = result["token"]
            orden.flow_order = result.get("flowOrder")
            orden.save()

            return JsonResponse(
                {
                    "success": True,
                    "url": result["url"],
                    "token": result["token"],
                    "orden_id": orden_id,
                }
            )

        except Exception as e:
            return JsonResponse(
                {"error": True, "message": f"Error interno: {str(e)}"},
                status=500,
            )

    # GET
    productos = Producto.objects.filter(activo=True)
    productos_data = []

    for p in productos:
        productos_data.append(
            {
                "id": p.id,
                "nombre": p.nombre,
                "precio": p.precio,
                "precio_formateado": formatear_precio(p.precio),
                "imagen": p.imagen.url if p.imagen else "",
            }
        )

    return render(
        request,
        "checkout.html",
        {"productos_json": json.dumps(productos_data), "DEBUG": settings.DEBUG},
    )


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
