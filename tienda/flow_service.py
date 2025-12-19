import hashlib
import requests
import urllib.parse
from django.conf import settings


class FlowService:
    """
    Servicio Flow CORRECTO
    - SHA256 plano
    - sin HMAC
    - sin timestamp en create_payment
    """

    def __init__(self, sandbox=True):
        self.api_key = settings.FLOW_API_KEY.strip()
        self.secret_key = settings.FLOW_SECRET_KEY.strip()

        self.base_url = (
            "https://sandbox.flow.cl/api"
            if sandbox else
            "https://www.flow.cl/api"
        )

        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales Flow no configuradas")

        print(">>> FlowService cargado correctamente <<<")

    def _generar_firma(self, params):
        params_firma = {k: v for k, v in params.items() if k != "s"}
        params_ordenados = sorted(params_firma.items())

        base_string = "&".join(f"{k}={v}" for k, v in params_ordenados)
        base_string += f"&secretKey={self.secret_key}"

        return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

    # ===============================
    # CREATE PAYMENT
    # ===============================
    def create_payment(self, datos):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(datos["commerceOrder"]),
            "subject": str(datos["subject"]),
            "currency": "CLP",
            "amount": int(datos["amount"]),
            "email": str(datos["email"]),
            "urlConfirmation": str(datos["urlConfirmation"]),
            "urlReturn": str(datos["urlReturn"]),
        }

        if datos.get("optional"):
            params["optional"] = str(datos["optional"])

        params["s"] = self._generar_firma(params)

        query = []
        for k, v in params.items():
            if k == "s":
                query.append(f"{k}={v}")
            else:
                query.append(f"{k}={urllib.parse.quote_plus(str(v))}")

        url = f"{self.base_url}/payment/create?" + "&".join(query)

        response = requests.get(url, timeout=30)
        return response.json()

    # ===============================
    # GET PAYMENT STATUS
    # ===============================
    def get_payment_status(self, token):
        params = {
            "apiKey": self.api_key,
            "token": token,
        }

        params["s"] = self._generar_firma(params)

        query = []
        for k, v in params.items():
            if k == "s":
                query.append(f"{k}={v}")
            else:
                query.append(f"{k}={urllib.parse.quote_plus(str(v))}")

        url = f"{self.base_url}/payment/getStatus?" + "&".join(query)

        response = requests.get(url, timeout=30)
        return response.json()
