import logging
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from tienda.models import Orden
from tienda.flow_service import FlowService

logger = logging.getLogger(__name__)


@csrf_exempt
def confirm_view(request):
    """
    Webhook que Flow llama cuando se completa un pago (exitoso o fallido).
    Flow siempre envía POST con el token. Debemos responder "OK" para que
    Flow sepa que recibimos la notificación.
    """
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)

    token = request.POST.get('token')
    if not token:
        logger.warning("confirm_view: token ausente en POST de Flow")
        return HttpResponseForbidden("Token missing")

    try:
        orden = Orden.objects.get(flow_token=token)
    except Orden.DoesNotExist:
        logger.error(f"confirm_view: no existe Orden con flow_token={token}")
        return HttpResponse("OK")

    try:
        flow = FlowService()
        estado = flow.get_payment_status(token)

        if not estado or "status" not in estado:
            logger.error(f"confirm_view: respuesta inválida de Flow para token={token}")
            return HttpResponse("OK")

        status_code = estado["status"]
        if status_code == 2:
            orden.estado = "pagado"
        elif status_code == 3:
            orden.estado = "rechazado"
        elif status_code == 4:
            orden.estado = "anulado"
        else:
            orden.estado = "pendiente"

        orden.save()
        logger.info(f"confirm_view: orden {orden.orden_id} → estado={orden.estado}")

    except Exception as e:
        logger.error(f"confirm_view: error procesando token={token}: {e}", exc_info=True)

    return HttpResponse("OK")