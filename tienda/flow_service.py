import requests
import hashlib
import hmac
from typing import Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self, environment=None):
        # Si no se pasa environment, lee de settings.py
        if environment is None:
            self.environment = "sandbox" if settings.FLOW_SANDBOX else "prod"
        else:
            self.environment = environment

        self.config = {
            "prod": {
                "base_url": "https://www.flow.cl/api/",
                "api_key": settings.FLOW_PROD_API_KEY,
                "secret_key": settings.FLOW_PROD_SECRET_KEY,
            },
            "sandbox": {
                "base_url": "https://sandbox.flow.cl/api/",
                "api_key": settings.FLOW_SANDBOX_API_KEY,
                "secret_key": settings.FLOW_SANDBOX_SECRET_KEY,
            }
        }
        
        # Limpieza de seguridad (.strip())
        self.api_key = str(self.config[self.environment]["api_key"]).strip()
        self.secret_key = str(self.config[self.environment]["secret_key"]).strip()
        self.base_url = self.config[self.environment]["base_url"]
        
        logger.info(f"FlowService inicializado en modo: {self.environment}")
    
    def _generate_signature(self, params: Dict) -> str:
        sorted_keys = sorted(params.keys())
        to_sign = ""
        for key in sorted_keys:
            if key == "s": continue
            value = str(params[key]).strip()
            to_sign += f"{key}{value}"

        return hmac.new(
            self.secret_key.encode("utf-8"),
            to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def create_payment(self, commerce_order, subject, amount, email, url_confirmation, url_return):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(commerce_order),
            "subject": subject,
            "currency": "CLP",
            "amount": int(amount),
            "email": email,
            "paymentMethod": 9, # 9 es Webpay
            "urlConfirmation": url_confirmation,
            "urlReturn": url_return,
        }
        params["s"] = self._generate_signature(params)

        try:
            response = requests.post(f"{self.base_url}payment/create", data=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Flow Create Error ({self.environment}): {response.text}")
            return None
        except Exception as e:
            logger.error(f"Flow Connection Error: {str(e)}")
            return None

    def get_payment_status(self, token: str) -> Optional[Dict]:
        params = {
            "apiKey": self.api_key,
            "token": str(token).strip()
        }
        params["s"] = self._generate_signature(params)
        
        try:
            response = requests.post(f"{self.base_url}payment/getStatus", data=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Flow Status Error: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Flow Status Exception: {str(e)}")
            return None