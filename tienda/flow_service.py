import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """Servicio para integración con Flow - VERSIÓN FINAL VERIFICADA"""
    
    def __init__(self, sandbox=False):
        self.sandbox = sandbox
        self.api_key = settings.FLOW_API_KEY.strip()  # ¡Quitar espacios!
        self.secret_key = settings.FLOW_SECRET_KEY.strip()  # ¡Quitar espacios!
        
        print(f"[INIT] API Key: {self.api_key}")
        print(f"[INIT] Secret Key: {self.secret_key[:10]}...")  # Solo primeros chars
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Flow API credentials not configured")
    
    @property
    def base_url(self):
        return "https://sandbox.flow.cl/api" if self.sandbox else "https://www.flow.cl/api"
    
    def _generate_signature(self, params):
        """
        GENERA FIRMA EXACTA según Flow
        """
        # 1. Remover 's' si existe
        params_to_sign = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar alfabéticamente (Flow es CASE SENSITIVE)
        sorted_params = sorted(params_to_sign.items())
        
        # 3. Crear string EXACTO
        string_to_sign = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        print(f"\n[FIRMA] String para firmar: '{string_to_sign}'")
        print(f"[FIRMA] Longitud string: {len(string_to_sign)}")
        print(f"[FIRMA] Secret Key (completa): {self.secret_key}")
        
        # 4. Calcular HMAC (¡ATENCIÓN! Flow requiere UTF-8)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        print(f"[FIRMA] Firma generada: {signature}")
        return signature
    
    def create_payment(self, order_data):
        """Crea pago en Flow - VERSIÓN CORREGIDA"""
        
        # ¡VERIFICAR API KEY!
        print(f"\n[PAYMENT] API Key desde settings: '{self.api_key}'")
        
        # Timestamp EN SEGUNDOS (no milisegundos)
        timestamp = str(int(time.time()))
        
        # PARÁMETROS EXACTOS como Flow los espera
        params = {
            'apiKey': self.api_key,  # ¡CASE SENSITIVE!
            'commerceOrder': str(order_data['commerceOrder']),
            'subject': str(order_data['subject']),
            'currency': 'CLP',
            'amount': str(order_data['amount']),  # String, no int
            'email': str(order_data['email']),
            'urlConfirmation': str(order_data['urlConfirmation']),
            'urlReturn': str(order_data['urlReturn']),
            'timestamp': timestamp  # ¡OBLIGATORIO!
        }
        
        # Opcionales
        if 'optional' in order_data:
            params['optional'] = str(order_data['optional'])
        
        # DEBUG: Mostrar parámetros ANTES de firmar
        print("\n[PARAMS] Parámetros antes de firmar:")
        for k, v in sorted(params.items()):
            print(f"  {k}: '{v}' (tipo: {type(v).__name__})")
        
        # Generar firma
        params['s'] = self._generate_signature(params)
        
        # Construir URL de prueba
        test_params = params.copy()
        # Crear versión segura para log (sin mostrar firma completa)
        test_params['s'] = test_params['s'][:10] + "..."
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/payment/create?{query_string}"
        
        print(f"\n[URL] URL generada (truncada):")
        print(url[:150] + "..." if len(url) > 150 else url)
        
        # ENVIAR PETICIÓN (Flow usa GET para create)
        try:
            print("\n[REQUEST] Enviando petición GET a Flow...")
            response = requests.get(
                url,
                timeout=30,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Django-Flow-Integration/1.0'
                }
            )
            
            print(f"[RESPONSE] Status: {response.status_code}")
            print(f"[RESPONSE] Body: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                # Intentar parsear error de Flow
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                
                return {
                    'error': True,
                    'status_code': response.status_code,
                    'message': 'Error en Flow API',
                    'detail': error_detail,
                    'debug_info': {
                        'api_key_used': self.api_key,
                        'timestamp_used': timestamp,
                        'url_short': url[:100] + "..."
                    }
                }
                
        except Exception as e:
            return {'error': True, 'message': str(e)}