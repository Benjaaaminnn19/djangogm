import requests
import hashlib
import hmac
from typing import Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FlowService:
    def __init__(self, environment="sandbox"):
        """
        Inicializa el servicio de Flow
        environment: "sandbox" o "prod"
        """
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
        
        self.environment = environment
        self.api_key = self.config[environment]["api_key"]
        self.secret_key = self.config[environment]["secret_key"]
        self.base_url = self.config[environment]["base_url"]
        
        # Log del ambiente
        logger.info(f"FlowService inicializado en modo: {environment}")
    
    def _generate_signature(self, params: Dict) -> str:
        """Genera la firma HMAC-SHA256 para los parámetros"""
        sorted_params = sorted(params.items())
        to_sign = "".join([f"{key}{value}" for key, value in sorted_params])
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def create_payment(self, 
                      commerce_order: str,
                      subject: str,
                      amount: int,
                      email: str,
                      url_confirmation: str,
                      url_return: str,
                      payment_method: int = 9) -> Optional[Dict]:
        """
        Crea un pago en Flow
        """
        params = {
            "apiKey": self.api_key,
            "commerceOrder": commerce_order,
            "subject": subject,
            "currency": "CLP",
            "amount": amount,
            "email": email,
            "paymentMethod": payment_method,
            "urlConfirmation": url_confirmation,
            "urlReturn": url_return
        }
        
        params["s"] = self._generate_signature(params)
        
        url = self.base_url + "payment/create"
        
        try:
            logger.info(f"Creando pago en Flow: {commerce_order} - ${amount} - {email}")
            response = requests.post(url, data=params, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Pago creado exitosamente: {commerce_order}")
                return response.json()
            else:
                logger.error(f"Flow Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Flow Request Exception: {str(e)}")
            return None
    
    def get_payment_status(self, token: str) -> Optional[Dict]:
        """
        Obtiene el estado de un pago
        """
        params = {
            "apiKey": self.api_key,
            "token": token
        }
        
        params["s"] = self._generate_signature(params)
        
        url = self.base_url + "payment/getStatus"
        
        try:
            logger.info(f"Consultando estado de pago: {token}")
            response = requests.post(url, data=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Estado de pago {token}: {data.get('status')}")
                return data
            else:
                logger.error(f"Flow Status Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Flow Status Exception: {str(e)}")
            return None