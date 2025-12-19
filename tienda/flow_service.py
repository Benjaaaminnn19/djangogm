import hashlib
import requests
import urllib.parse
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
        # 1. Quitar firma
        params = {k: str(v) for k, v in params.items() if k != "s"}

        # 2. Ordenar alfabéticamente
        ordered = sorted(params.items())

        # 3. Base string EXACTA
        base_string = "&".join(f"{k}={v}" for k, v in ordered)
        base_string += f"&secretKey={self.secret_key}"

        # 4. SHA256 plano
        return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

    # -------------------------------------------------

    def crear_pago(self, datos):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(datos["commerceOrder"]),
            "subject": str(datos["subject"]),
            "currency": "CLP",
            "amount": str(datos["amount"]),   # 🔴 STRING
            "email": str(datos["email"]),
            "urlConfirmation": str(datos["urlConfirmation"]),
            "urlReturn": str(datos["urlReturn"]),
        }

        # Firma
        params["s"] = self._generar_firma(params)

        # URL encode SOLO para la request
        query = []
        for k, v in params.items():
            if k == "s":
                query.append(f"{k}={v}")
            else:
                query.append(f"{k}={urllib.parse.quote_plus(v)}")

        url = f"{self.base_url}/payment/create?" + "&".join(query)

        response = requests.get(url, timeout=30)
        return response.json()

    # -------------------------------------------------

    def obtener_estado_pago(self, token):
        params = {
            "apiKey": self.api_key,
            "token": str(token),
        }

        params["s"] = self._generar_firma(params)

        query = []
        for k, v in params.items():
            if k == "s":
                query.append(f"{k}={v}")
            else:
                query.append(f"{k}={urllib.parse.quote_plus(v)}")

        url = f"{self.base_url}/payment/getStatus?" + "&".join(query)

        response = requests.get(url, timeout=30)
        return response.json()
