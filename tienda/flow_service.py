# flow_service_final.py
import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """Servicio Flow - VERSIÓN VALIDADA"""
    
    def __init__(self, sandbox=False):
        """
        sandbox: True para pruebas, False para producción
        """
        self.sandbox = sandbox
        
        # Obtener y limpiar credenciales
        self.api_key = getattr(settings, 'FLOW_API_KEY', '').strip()
        self.secret_key = getattr(settings, 'FLOW_SECRET_KEY', '').strip()
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales de Flow no configuradas")
        
        # DEBUG
        print(f"[FLOW] API Key: {self.api_key[:8]}...")
        print(f"[FLOW] Sandbox: {self.sandbox}")
    
    @property
    def base_url(self):
        """URL base según ambiente"""
        return "https://sandbox.flow.cl/api" if self.sandbox else "https://www.flow.cl/api"
    
    def _generate_signature(self, params):
        """
        Genera firma HMAC-SHA256 para Flow.
        
        IMPORTANTE: Los valores deben estar URL-encoded para la firma,
        pero NO la firma misma.
        """
        # 1. Excluir parámetro 's' si existe
        params_to_sign = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar alfabéticamente
        sorted_params = sorted(params_to_sign.items())
        
        # 3. Crear string con valores URL-encoded
        # Flow espera: key=urlencode(value)
        string_parts = []
        for key, value in sorted_params:
            # URL-encode el valor (excepto para la firma misma)
            encoded_value = urllib.parse.quote(str(value), safe='')
            string_parts.append(f"{key}={encoded_value}")
        
        string_to_sign = '&'.join(string_parts)
        
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
            order_data: dict con:
                - commerceOrder (str): ID orden única
                - subject (str): Descripción
                - amount (int): Monto en CLP
                - email (str): Email cliente
                - urlConfirmation (str): URL webhook
                - urlReturn (str): URL retorno
                
        Returns:
            dict: Respuesta de Flow
        """
        # Validar datos requeridos
        required = ['commerceOrder', 'subject', 'amount', 'email', 
                   'urlConfirmation', 'urlReturn']
        for field in required:
            if field not in order_data:
                return {
                    'error': True,
                    'message': f'Falta campo requerido: {field}'
                }
        
        # 1. Timestamp actual (segundos UNIX)
        timestamp = str(int(time.time()))
        
        # 2. Parámetros base (todos como strings)
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(order_data['commerceOrder']),
            'subject': str(order_data['subject']),
            'currency': 'CLP',
            'amount': str(order_data['amount']),
            'email': str(order_data['email']),
            'urlConfirmation': str(order_data['urlConfirmation']),
            'urlReturn': str(order_data['urlReturn']),
            'timestamp': timestamp
        }
        
        # 3. Campos opcionales
        optional_fields = ['optional', 'paymentMethod', 'timeout']
        for field in optional_fields:
            if field in order_data and order_data[field]:
                params[field] = str(order_data[field])
        
        # 4. Generar firma
        params['s'] = self._generate_signature(params)
        
        # 5. Construir URL para GET
        # Para la URL final, usar quote_plus para mejor legibilidad
        url_parts = []
        for key, value in params.items():
            if key == 's':
                # La firma ya está en hex, no necesita encoding extra
                url_parts.append(f"{key}={value}")
            else:
                # Usar quote_plus para convertir espacios a +
                encoded_value = urllib.parse.quote_plus(str(value))
                url_parts.append(f"{key}={encoded_value}")
        
        query_string = '&'.join(url_parts)
        url = f"{self.base_url}/payment/create?{query_string}"
        
        # 6. Enviar petición GET
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Django-Flow/1.0'
                }
            )
            
            # 7. Procesar respuesta
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    return {
                        'error': True,
                        'message': 'Respuesta JSON inválida de Flow',
                        'raw': response.text[:500]
                    }
            else:
                # Intentar obtener error específico de Flow
                error_info = {'status': response.status_code}
                try:
                    flow_error = response.json()
                    error_info.update(flow_error)
                except:
                    error_info['raw'] = response.text[:500]
                
                error_info['error'] = True
                error_info['message'] = 'Error en API Flow'
                return error_info
                
        except requests.exceptions.Timeout:
            return {'error': True, 'message': 'Timeout conectando a Flow'}
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': f'Error de conexión: {str(e)}'}