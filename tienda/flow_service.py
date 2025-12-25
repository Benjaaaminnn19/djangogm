# tienda/flow_service.py
import requests
import hashlib
import hmac

class FlowService:
    def __init__(self, environment="sandbox"):
        FLOW_CONFIG = {
            "prod": {
                "base_url": "https://www.flow.cl/api/",
                "api_key": "TU_API_KEY_PROD",
                "secret_key": "TU_SECRET_KEY_PROD",
            },
            "sandbox": {
                "base_url": "https://sandbox.flow.cl/api/",
                "api_key": "346F180A-05F3-4C5A-8846-20LEBCB5EF2B",       # ← Pon aquí tu API Key real del sandbox
                "secret_key": "346F180A-05F3-4C5A-8846-20LEBCB5EF2B", # ← Pon aquí tu Secret Key real del sandbox
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

        # Ordenar y firmar
        sorted_params = sorted(params.items())
        to_sign = "".join([f"{k}{v}" for k, v in sorted_params])
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        params["s"] = signature

        response = requests.post(self.create_url, data=params)
        return response.json() if response.status_code == 200 else None