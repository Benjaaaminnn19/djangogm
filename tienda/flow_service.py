# flow_service.py - Versión REAL para tu gimnasio
import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """Servicio Flow para Gimnasio - Sin complicaciones"""
    
    def __init__(self):
        # Obtener URL base desde settings (definida en .env o Railway)
        self.base_url = getattr(settings, 'FLOW_BASE_URL', 'https://www.flow.cl/api')
        
        # Tus claves (las mismas siempre)
        self.api_key = settings.FLOW_API_KEY.strip()
        self.secret_key = settings.FLOW_SECRET_KEY.strip()
        
        # Debug útil
        print(f"🔧 FlowService: {self.base_url}")
        print(f"   Usando API Key: {self.api_key[:8]}...")
        
    def _crear_firma(self, params):
        """Crea la firma CORRECTA para Flow"""
        # 1. Quitar 's' si existe
        params_sin_firma = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar A-Z
        params_ordenados = sorted(params_sin_firma.items())
        
        # 3. Crear string clave=valor_codificado
        partes = []
        for clave, valor in params_ordenados:
            # ¡ESTO ES LO MÁS IMPORTANTE!
            valor_codificado = urllib.parse.quote(str(valor), safe='')
            partes.append(f"{clave}={valor_codificado}")
        
        string_para_firmar = '&'.join(partes)
        
        # DEBUG: Esto te mostrará EXACTAMENTE qué se está firmando
        print("\n📄 STRING para FIRMAR:")
        print(string_para_firmar)
        print("=" * 50)
        
        # 4. Calcular HMAC
        firma = hmac.new(
            self.secret_key.encode('utf-8'),
            string_para_firmar.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        print(f"✅ FIRMA generada: {firma}")
        return firma
    
    def crear_pago(self, orden):
        """Crea pago en Flow - Simple y directo"""
        
        # 1. Preparar parámetros OBLIGATORIOS
        timestamp = str(int(time.time()))
        
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(orden['commerceOrder']),
            'subject': str(orden['subject']),
            'currency': 'CLP',
            'amount': str(orden['amount']),  # ¡Como string!
            'email': str(orden['email']),
            'urlConfirmation': str(orden['urlConfirmation']),
            'urlReturn': str(orden['urlReturn']),
            'timestamp': timestamp,  # ¡NO OLVIDAR!
        }
        
        # 2. Generar firma
        params['s'] = self._crear_firma(params)
        
        # 3. Construir URL FINAL
        partes_url = []
        for clave, valor in params.items():
            if clave == 's':
                partes_url.append(f"{clave}={valor}")
            else:
                # Para la URL, usar quote_plus (espacios → +)
                valor_codificado = urllib.parse.quote_plus(str(valor))
                partes_url.append(f"{clave}={valor_codificado}")
        
        url_completa = f"{self.base_url}/payment/create?{'&'.join(partes_url)}"
        
        print(f"\n🌐 URL enviada a Flow (inicio):")
        print(url_completa[:150] + "...")
        
        # 4. Enviar a Flow (usa GET)
        try:
            respuesta = requests.get(url_completa, timeout=30)
            print(f"\n📨 Respuesta de Flow: {respuesta.status_code}")
            
            if respuesta.status_code == 200:
                print("✅ ¡PAGO CREADO EXITOSAMENTE!")
                return respuesta.json()
            else:
                print(f"❌ Error {respuesta.status_code}: {respuesta.text}")
                return {'error': True, 'detalle': respuesta.text}
                
        except Exception as e:
            print(f"🔥 Error de conexión: {e}")
            return {'error': True, 'detalle': str(e)}