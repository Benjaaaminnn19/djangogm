import hashlib
import requests
import urllib.parse
import time
from django.conf import settings


class FlowService:
    """
    Servicio Flow CORRECTO
    - SHA256 plano (NO HMAC)
    - Firma SIN url-encode
    - URL con encode
    - timestamp OBLIGATORIO
    """

    def __init__(self, sandbox=True):
        self.api_key = settings.FLOW_API_KEY.strip()
        self.secret_key = settings.FLOW_SECRET_KEY.strip()

        if sandbox:
            self.base_url = "https://sandbox.flow.cl/api"
        else:
            self.base_url = "https://www.flow.cl/api"

        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales Flow no configuradas")

        print(">>> FlowService cargado correctamente <<<")

    def _generar_firma(self, params):
        # Excluir firma
        params_firma = {k: v for k, v in params.items() if k != "s"}

        # Ordenar alfabéticamente
        params_ordenados = sorted(params_firma.items())

        # Crear string base SIN URL ENCODE
        base_string = "&".join(f"{k}={v}" for k, v in params_ordenados)
        base_string += f"&secretKey={self.secret_key}"

        # DEBUG (opcional)
        print("BASE STRING:", base_string)

        return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

    def crear_pago(self, datos):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(datos["commerceOrder"]),
            "subject": str(datos["subject"]),
            "currency": "CLP",
            "amount": str(datos["amount"]),  # STRING
            "email": str(datos["email"]),
            "urlConfirmation": str(datos["urlConfirmation"]),
            "urlReturn": str(datos["urlReturn"]),
            "timestamp": str(int(time.time())),  # 🔥 OBLIGATORIO
        }

        if datos.get("optional"):
            params["optional"] = str(datos["optional"])

        # Generar firma
        params["s"] = self._generar_firma(params)

        # Construir query (AQUÍ sí va encode)
        query = []
        for k, v in params.items():
            if k == "s":
                query.append(f"{k}={v}")
            else:
                query.append(f"{k}={urllib.parse.quote_plus(str(v))}")

        url = f"{self.base_url}/payment/create?" + "&".join(query)

        response = requests.get(url, timeout=30)
        return response.json()

    def obtener_estado_pago(self, token):
        params = {
            "apiKey": self.api_key,
            "token": token,
            "timestamp": str(int(time.time())),
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
