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
                "secret_key": "d94486228bf9290b6116ee24cd9c93645318d9c0"  # ← CLAVE SECRETA LARGA
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

        # Generar firma
        sorted_params = sorted(params.items())
        to_sign = "".join([f"{key}{value}" for key, value in sorted_params])
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        params["s"] = signature

        # Debug temporal (verás esto en los logs de Railway)
        logger.info("=== FLOW REQUEST ===")
        logger.info("URL: %s", self.create_url)
        logger.info("Params: %s", params)
        logger.info("String to sign: %s", to_sign)
        logger.info("Signature: %s", signature)

        response = requests.post(self.create_url, data=params)

        logger.info("Flow Status Code: %s", response.status_code)
        logger.info("Flow Response: %s", response.text)

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                logger.error("Respuesta no es JSON válido: %s", response.text)
                return None
        else:
            logger.error("Error HTTP %s: %s", response.status_code, response.text)
            return None