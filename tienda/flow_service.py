import hashlib
import requests
from django.conf import settings


class FlowService:

    def __init__(self, sandbox=True):
        self.api_key = settings.FLOW_API_KEY.strip()
        self.secret_key = settings.FLOW_SECRET_KEY.strip()

        self.base_url = (
            "https://sandbox.flow.cl/api"
            if sandbox
            else "https://www.flow.cl/api"
        )

        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales Flow no configuradas")

    # -------------------------------------------------

    def _generar_firma(self, params):
        params = {k: str(v) for k, v in params.items() if k != "s"}
        ordered = sorted(params.items())

        base_string = "&".join(f"{k}={v}" for k, v in ordered)
        base_string += f"&secretKey={self.secret_key}"

        return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

    # -------------------------------------------------

    def crear_pago(self, datos):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(datos["commerceOrder"]),
            "subject": str(datos["subject"]),
            "currency": "CLP",
            "amount": str(datos["amount"]),
            "email": str(datos["email"]),
            "urlConfirmation": str(datos["urlConfirmation"]),
            "urlReturn": str(datos["urlReturn"]),
        }

        params["s"] = self._generar_firma(params)

        # 🔴 POST (NO GET)
        response = requests.post(
            f"{self.base_url}/payment/create",
            data=params,
            timeout=30
        )

        return response.json()

    # -------------------------------------------------

    def obtener_estado_pago(self, token):
        params = {
            "apiKey": self.api_key,
            "token": str(token),
        }

        params["s"] = self._generar_firma(params)

        response = requests.post(
            f"{self.base_url}/payment/getStatus",
            data=params,
            timeout=30
        )

        return response.json()
