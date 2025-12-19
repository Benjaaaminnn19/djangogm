import hmac
import hashlib
import requests
from django.conf import settings
from urllib.parse import urlencode

class FlowService:
    """Servicio para integración con Flow"""
    
    def __init__(self):
        self.api_key = settings.FLOW_API_KEY
        self.secret_key = settings.FLOW_SECRET_KEY
        self.api_url = settings.FLOW_API_URL
    
    def generate_signature(self, params):
        """Genera la firma para autenticar la petición"""
        # Ordenar parámetros alfabéticamente
        sorted_params = sorted(params.items())
        # Crear string con formato key=value&key=value
        params_string = urlencode(sorted_params)
        # Crear firma HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            params_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def create_payment(self, order_data):
        """
        Crea un pago en Flow
        
        order_data debe contener:
        - commerceOrder: ID único de tu orden
        - subject: Descripción del pago
        - amount: Monto total
        - email: Email del cliente
        - urlConfirmation: URL de confirmación en tu servidor
        - urlReturn: URL a donde vuelve el cliente después de pagar
        """
        params = {
            'apiKey': self.api_key,
            'commerceOrder': order_data['commerceOrder'],
            'subject': order_data['subject'],
            'currency': 'CLP',
            'amount': int(order_data['amount']),
            'email': order_data['email'],
            'urlConfirmation': order_data['urlConfirmation'],
            'urlReturn': order_data['urlReturn'],
        }
        
        # Agregar campos opcionales si existen
        if 'optional' in order_data:
            params['optional'] = order_data['optional']
        
        # Generar firma
        params['s'] = self.generate_signature(params)
        
        # Hacer petición a Flow
        try:
            response = requests.post(
                f"{self.api_url}/payment/create",
                data=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_payment_status(self, token):
        """Obtiene el estado de un pago usando el token"""
        params = {
            'apiKey': self.api_key,
            'token': token
        }
        params['s'] = self.generate_signature(params)
        
        try:
            response = requests.get(
                f"{self.api_url}/payment/getStatus",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}