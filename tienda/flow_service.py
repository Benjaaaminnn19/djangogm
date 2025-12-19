import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """Servicio para integración con Flow - VERSIÓN FINAL"""
    
    def __init__(self, sandbox=False):
        """
        Inicializa el servicio Flow.
        
        Args:
            sandbox (bool): True para ambiente de pruebas, False para producción
        """
        self.sandbox = sandbox
        
        # Obtener credenciales desde settings
        self.api_key = settings.FLOW_API_KEY
        self.secret_key = settings.FLOW_SECRET_KEY
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Flow API credentials not configured in settings")
    
    @property
    def base_url(self):
        """Devuelve la URL base según el ambiente"""
        if self.sandbox:
            return "https://sandbox.flow.cl/api"
        return "https://www.flow.cl/api"
    
    def _generate_signature(self, params):
        """
        Genera firma HMAC-SHA256 según especificación de Flow.
        
        Args:
            params (dict): Parámetros a firmar
            
        Returns:
            str: Firma HMAC-SHA256 en mayúsculas
        """
        # 1. Filtrar parámetro 's' si existe
        params_to_sign = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar alfabéticamente por nombre de parámetro
        sorted_params = sorted(params_to_sign.items())
        
        # 3. Crear string en formato key=value&key=value
        string_to_sign = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # DEBUG (quitar en producción)
        if getattr(settings, 'DEBUG', False):
            print(f"[FLOW DEBUG] String para firmar: {string_to_sign}")
        
        # 4. Calcular HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature
    
    def create_payment(self, order_data):
        """
        Crea un pago en Flow.
        
        Args:
            order_data (dict): {
                'commerceOrder': str,       # ID único de la orden
                'subject': str,             # Descripción del pago
                'amount': int,              # Monto en CLP
                'email': str,               # Email del cliente
                'urlConfirmation': str,     # URL de confirmación
                'urlReturn': str,           # URL de retorno
                'optional': str (opcional), # Datos adicionales
            }
            
        Returns:
            dict: Respuesta de Flow
        """
        # Validar datos mínimos
        required_fields = ['commerceOrder', 'subject', 'amount', 
                          'email', 'urlConfirmation', 'urlReturn']
        for field in required_fields:
            if field not in order_data:
                return {
                    'error': True,
                    'message': f'Campo requerido faltante: {field}'
                }
        
        # 1. Generar timestamp (segundos UNIX)
        timestamp = str(int(time.time()))
        
        # 2. Preparar parámetros (todos como strings)
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(order_data['commerceOrder']),
            'subject': str(order_data['subject']),
            'currency': 'CLP',
            'amount': str(order_data['amount']),
            'email': str(order_data['email']),
            'urlConfirmation': str(order_data['urlConfirmation']),
            'urlReturn': str(order_data['urlReturn']),
            'timestamp': timestamp  # ¡IMPORTANTE!
        }
        
        # 3. Campos opcionales
        optional_fields = ['optional', 'paymentMethod', 'timeout', 'merchantId']
        for field in optional_fields:
            if field in order_data and order_data[field]:
                params[field] = str(order_data[field])
        
        # 4. Generar firma
        params['s'] = self._generate_signature(params)
        
        # DEBUG en desarrollo
        if getattr(settings, 'DEBUG', False):
            print("\n[FLOW DEBUG] === Creando Pago ===")
            print(f"URL Base: {self.base_url}")
            print("Parámetros enviados:")
            for key, value in sorted(params.items()):
                safe_value = value if key != 's' else f"{value[:10]}..."
                print(f"  {key}: {safe_value}")
        
        # 5. Construir URL para GET
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/payment/create?{query_string}"
        
        # 6. Enviar petición GET (Flow usa GET para este endpoint)
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={'Accept': 'application/json'}
            )
            
            # DEBUG
            if getattr(settings, 'DEBUG', False):
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
            
            # 7. Procesar respuesta
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    return {
                        'error': True,
                        'message': 'Respuesta JSON inválida',
                        'raw_response': response.text
                    }
            else:
                return {
                    'error': True,
                    'status_code': response.status_code,
                    'message': 'Error en la API de Flow',
                    'detail': response.text,
                    'url': url[:200] + "..." if len(url) > 200 else url
                }
                
        except requests.exceptions.Timeout:
            return {
                'error': True,
                'message': 'Timeout al conectar con Flow'
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Error de conexión: {str(e)}'
            }
    
    def get_payment_status(self, token):
        """
        Obtiene el estado de un pago.
        
        Args:
            token (str): Token del pago
            
        Returns:
            dict: Estado del pago
        """
        timestamp = str(int(time.time()))
        
        params = {
            'apiKey': self.api_key,
            'token': token,
            'timestamp': timestamp
        }
        
        params['s'] = self._generate_signature(params)
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/payment/getStatus?{query_string}"
        
        try:
            response = requests.get(url, timeout=30)
            return response.json()
        except Exception as e:
            return {'error': True, 'message': str(e)}
    
    def verify_notification(self, params):
        """
        Verifica una notificación entrante de Flow.
        
        Args:
            params (dict): Parámetros recibidos en la notificación
            
        Returns:
            bool: True si la firma es válida
        """
        if 's' not in params:
            return False
        
        received_signature = params['s']
        calculated_signature = self._generate_signature(params)
        
        return received_signature == calculated_signature