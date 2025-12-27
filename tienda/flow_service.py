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
                "secret_key": "8ede55f7557f210c0497596ef4b6fc039825d30a"  # ← CLAVE SECRETA LARGA
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

    # === CÁLCULO DE FIRMA OFICIAL ===
    # 1. Ordenar parámetros alfabéticamente por clave
        sorted_items = sorted(params.items(), key=lambda x: x[0])
    
    # 2. Concatenar clave + valor sin separadores
        to_sign = "".join([f"{k}{v}" for k, v in sorted_items])
    
    # 3. HMAC-SHA256 con la Secret Key
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    # 4. Agregar la firma
        params["s"] = signature

    # Debug (mantén esto temporalmente)
  
        logger = logging.getLogger(__name__)
        logger.info("=== FLOW DEBUG ===")
        logger.info("To sign: %s", to_sign)
        logger.info("Signature generada: %s", signature)
        logger.info("Params finales: %s", params)

        response = requests.post(self.create_url, data=params)

        logger.info("Status: %s", response.status_code)
        logger.info("Response: %s", response.text)

        if response.status_code == 200:
            try:
                return response.json()
            except:
                return None
        else:
            return None