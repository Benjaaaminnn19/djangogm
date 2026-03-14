import requests
import hashlib
import hmac
from typing import Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FlowService:
    
    BASE_URLS = {
        "sandbox": "https://sandbox.flow.cl/api/",
        "prod": "https://www.flow.cl/api/",
    }

    def __init__(self, environment=None):
        if environment is None:
            self.environment = "sandbox" if settings.FLOW_SANDBOX else "prod"
        else:
            self.environment = environment

        if self.environment not in self.BASE_URLS:
            raise ValueError(f"Entorno Flow inválido: '{self.environment}'. Usa 'sandbox' o 'prod'.")

        # ← FIX: base_url se toma del dict de clase, nunca puede quedar vacío
        self.base_url = self.BASE_URLS[self.environment]

        if self.environment == "sandbox":
            self.api_key    = str(settings.FLOW_SANDBOX_API_KEY).strip()
            self.secret_key = str(settings.FLOW_SANDBOX_SECRET_KEY).strip()
        else:
            self.api_key    = str(settings.FLOW_PROD_API_KEY).strip()
            self.secret_key = str(settings.FLOW_PROD_SECRET_KEY).strip()

        # Validación temprana: avisa en logs si las credenciales están vacías
        if not self.api_key or not self.secret_key:
            logger.warning(
                f"FlowService ({self.environment}): api_key o secret_key están vacíos. "
                "Revisa tus variables de entorno."
            )

        logger.info(f"FlowService inicializado en modo: {self.environment} | base_url: {self.base_url}")

    def _generate_signature(self, params: Dict) -> str:
        sorted_keys = sorted(params.keys())
        to_sign = ""
        for key in sorted_keys:
            if key == "s":
                continue
            value = str(params[key]).strip()
            to_sign += f"{key}{value}"

        return hmac.new(
            self.secret_key.encode("utf-8"),
            to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    def create_payment(self, commerce_order, subject, amount, email,
                       url_confirmation, url_return):
        params = {
            "apiKey":          self.api_key,
            "commerceOrder":   str(commerce_order),
            "subject":         subject,
            "currency":        "CLP",
            "amount":          int(amount),       # siempre int
            "email":           email,
            "paymentMethod":   9,
            "urlConfirmation": url_confirmation,
            "urlReturn":       url_return,
        }
        params["s"] = self._generate_signature(params)

        url = f"{self.base_url}payment/create"
        logger.info(f"Flow create_payment → POST {url} | order={commerce_order} | amount={amount}")

        try:
            response = requests.post(url, data=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Flow Create Error ({self.environment}) {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Flow Connection Error: {str(e)}")
            return None

    def get_payment_status(self, token: str) -> Optional[Dict]:
        params = {
            "apiKey": self.api_key,
            "token":  str(token).strip(),
        }
        params["s"] = self._generate_signature(params)

        url = f"{self.base_url}payment/getStatus"

        try:
            response = requests.post(url, data=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Flow Status Error: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Flow Status Exception: {str(e)}")
            return None