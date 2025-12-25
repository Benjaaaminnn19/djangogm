# tienda/flow_service.py
import requests
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self, environment="sandbox"):
        FLOW_CONFIG = {
            "prod": {
                "base_url": "https://www.flow.cl/api/",
                "api_key": "TU_API_KEY_DE_PRODUCCION",           # Cambiar cuando pases a real
                "secret_key": "TU_SECRET_KEY_DE_PRODUCCION",
            },
            "sandbox": {
                "base_url": "https://sandbox.flow.cl/api/",
                "api_key": "346F180A-05F3-4C5A-8846-20LEBCB5EF2B",     # ← CLAVE CORRECTA
                "secret_key": "346F180A-05F3-4C5A-8846-20LEBCB5EF2B"  # ← CLAVE SECRETA LARGA
            }
        }

        config = FLOW_CONFIG[environment]
        self.api_key = config["api_key"]
        self.secret_key = config["secret_key"]
        self.create_url = config["base_url"] + "payment/create"

    def create_payment(self, order_data):
        params = {
            "apiKey": self.api_key,
            "commerceOrder": order_data["commerceOrder"],
            "subject": order_data["subject"],
            "currency": "CLP",
            "amount": order_data["amount"],
            "email": order_data["email"],
            "paymentMethod": 9,
            "urlConfirmation": order_data["urlConfirmation"],
            "urlReturn": order_data["urlReturn"]
        }

        sorted_params = sorted(params.items())
        to_sign = "".join([f"{key}{value}" for key, value in sorted_params])
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        params["s"] = signature

   
        logger = logging.getLogger(__name__)
        logger.info(f"Flow URL: {self.create_url}")
        logger.info(f"Params: {params}")
        logger.info(f"String to sign: {to_sign}")
        logger.info(f"Signature: {signature}")

        try:
            response = requests.post(self.create_url, data=params, timeout=30)
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text, "status": response.status_code}
        except Exception as e:
            logger.error(f"Error de conexión: {str(e)}")
            return None