import requests
import hashlib
import hmac
from typing import Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self, environment=None):
        """
        Si environment es None, usamos lo que diga settings.FLOW_SANDBOX
        """
        # Determinar ambiente automáticamente si no se pasa uno
        if environment is None:
            env_type = "sandbox" if settings.FLOW_SANDBOX else "prod"
        else:
            env_type = environment

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
        
        self.environment = env_type
        # IMPORTANTE: .strip() elimina espacios accidentales de las keys del .env
        self.api_key = str(self.config[env_type]["api_key"]).strip()
        self.secret_key = str(self.config[env_type]["secret_key"]).strip()
        self.base_url = self.config[env_type]["base_url"]
        
        logger.info(f"FlowService inicializado en modo: {self.environment}")
    
    def _generate_signature(self, params: Dict) -> str:
        """
        Genera la firma digital requerida por Flow
        """
        # 1. Ordenar los parámetros alfabéticamente por llave
        sorted_keys = sorted(params.keys())

        # 2. Concatenar llave+valor (excluyendo la firma 's')
        to_sign = ""
        for key in sorted_keys:
            if key == "s":
                continue
            # Aseguramos que el valor sea string y no tenga espacios nulos
            value = str(params[key]).strip()
            to_sign += f"{key}{value}"

        # 3. Firmar usando HMAC SHA256
        return hmac.new(
            self.secret_key.encode("utf-8"),
            to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def create_payment(
        self,
        commerce_order: str,
        subject: str,
        amount: int,
        email: str,
        url_confirmation: str,
        url_return: str,
        payment_method: int = 9
    ):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": str(commerce_order),
            "subject": subject,
            "currency": "CLP",
            "amount": int(amount),
            "email": email,
            "paymentMethod": payment_method,
            "urlConfirmation": url_confirmation,
            "urlReturn": url_return,
        }

        # Generar firma con los parámetros finales
        params["s"] = self._generate_signature(params)

        try:
            response = requests.post(
                f"{self.base_url}payment/create",
                data=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            logger.error(f"Flow Error ({self.environment}): {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error de conexión con Flow: {str(e)}")
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
            return None
        except Exception as e:
            logger.error(f"Flow Status Exception: {str(e)}")
            return None