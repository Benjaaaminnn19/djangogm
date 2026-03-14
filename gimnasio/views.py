# proyecto/views.py (raíz del proyecto)
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
import requests
# Importa tus modelos o lo que necesites para actualizar la orden

@csrf_exempt  # Imprescindible para webhooks externos
def confirm_view(request):
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)

    # Aquí obtienes los datos que envía Flow
    token = request.POST.get('token')

    if not token:
        return HttpResponseForbidden("Token missing")

    # === OPCIÓN 1: Verificar firma (recomendado para seguridad) ===
    # Flow envía los mismos parámetros que usaste en create, más el token
    # Debes reconstruir la firma y compararla con la que envía Flow en "s"
    # (Código completo te lo paso si lo necesitas)

    # === OPCIÓN 2: Consultar directamente el estado (más simple y suficiente en muchos casos) ===
    # Llamas a payment/getStatus con tu API Key y el token
    status_url = "https://www.flow.cl/api"  # Cambia a prod cuando pases
    payload = {
        "apiKey": "346F180A-05F3-4C5A-8846-20LEBCB5EF2B",
        "token": token
    }
    # Firma para getStatus (similar a create)
    # ... (código de firma)
    response = requests.post(status_url, data=payload)
    if response.status_code == 200:
        data = response.json()
        # Aquí procesas: si data['status'] == 1 (pendiente), 2 (pagado), etc.
        # Actualizas tu orden en la DB, activas el plan, envías email, etc.

    return HttpResponse("OK")  # ¡Siempre responder "OK"!