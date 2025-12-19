import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """Servicio Flow para procesar pagos - Versión corregida"""
    
    def __init__(self):
        # Obtener credenciales desde settings
        self.api_key = getattr(settings, 'FLOW_API_KEY', '').strip()
        self.secret_key = getattr(settings, 'FLOW_SECRET_KEY', '').strip()
        self.base_url = getattr(settings, 'FLOW_API_URL', 'https://www.flow.cl/api').strip()
        
        # Validar credenciales
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "❌ Credenciales de Flow no configuradas. "
                "Verifica FLOW_API_KEY y FLOW_SECRET_KEY en tus variables de entorno."
            )
        
        # Log de configuración (solo primeros caracteres por seguridad)
        print(f"✅ FlowService inicializado")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key: {self.api_key[:8]}...")
        print(f"   Secret Key: {self.secret_key[:8]}...")
    
    def _generar_firma(self, params):
        """
        Genera la firma HMAC-SHA256 requerida por Flow.
        
        Proceso:
        1. Excluir el parámetro 's' (firma)
        2. Ordenar parámetros alfabéticamente
        3. Construir string: key1=value1&key2=value2 (con valores URL-encoded)
        4. Calcular HMAC-SHA256
        """
        # 1. Excluir 's' si existe
        params_sin_firma = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar alfabéticamente
        params_ordenados = sorted(params_sin_firma.items())
        
        # 3. Construir string con valores URL-encoded
        partes = []
        for clave, valor in params_ordenados:
            # URL encode con safe='' para codificar TODO (incluso espacios → %20)
            valor_codificado = urllib.parse.quote(str(valor), safe='')
            partes.append(f"{clave}={valor_codificado}")
        
        string_a_firmar = '&'.join(partes)
        
        # DEBUG: Mostrar string que se va a firmar
        if settings.DEBUG:
            print(f"\n🔐 STRING A FIRMAR:")
            print(f"{string_a_firmar}")
            print("=" * 80)
        
        # 4. Calcular HMAC-SHA256
        firma = hmac.new(
            self.secret_key.encode('utf-8'),
            string_a_firmar.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        print(f"✅ Firma generada: {firma}")
        
        return firma
    
    def crear_pago(self, datos_orden):
        """
        Crea un pago en Flow.
        
        Args:
            datos_orden (dict): Datos de la orden con los siguientes campos:
                - commerceOrder (str): ID único de tu orden
                - subject (str): Descripción del pago
                - amount (int): Monto en pesos chilenos
                - email (str): Email del pagador
                - urlConfirmation (str): URL webhook para confirmar pago
                - urlReturn (str): URL donde vuelve el usuario después de pagar
        
        Returns:
            dict: Respuesta de Flow con 'url', 'token', etc.
                  o {'error': True, 'message': '...'} si falla
        """
        # Validar campos requeridos
        campos_requeridos = ['commerceOrder', 'subject', 'amount', 'email', 
                            'urlConfirmation', 'urlReturn']
        
        for campo in campos_requeridos:
            if campo not in datos_orden:
                return {
                    'error': True,
                    'message': f'Falta el campo requerido: {campo}'
                }
        
        # Preparar parámetros
        timestamp = str(int(time.time()))
        
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(datos_orden['commerceOrder']),
            'subject': str(datos_orden['subject']),
            'currency': 'CLP',
            'amount': str(datos_orden['amount']),
            'email': str(datos_orden['email']),
            'urlConfirmation': str(datos_orden['urlConfirmation']),
            'urlReturn': str(datos_orden['urlReturn']),
            'timestamp': timestamp,
        }
        
        # Agregar parámetro opcional si existe
        if 'optional' in datos_orden and datos_orden['optional']:
            params['optional'] = str(datos_orden['optional'])
        
        # Generar firma
        params['s'] = self._generar_firma(params)
        
        # Construir URL completa
        partes_url = []
        for clave, valor in params.items():
            if clave == 's':
                # La firma NO se codifica
                partes_url.append(f"{clave}={valor}")
            else:
                # Otros parámetros sí se codifican (espacios → +)
                valor_codificado = urllib.parse.quote_plus(str(valor))
                partes_url.append(f"{clave}={valor_codificado}")
        
        query_string = '&'.join(partes_url)
        url_completa = f"{self.base_url}/payment/create?{query_string}"
        
        # DEBUG: Mostrar URL (truncada por seguridad)
        if settings.DEBUG:
            print(f"\n🌐 URL de petición a Flow:")
            print(f"{url_completa[:200]}...")
            print("=" * 80)
        
        # Hacer petición GET a Flow
        try:
            print(f"\n📤 Enviando petición a Flow...")
            respuesta = requests.get(url_completa, timeout=30)
            
            print(f"📥 Respuesta recibida: {respuesta.status_code}")
            
            if respuesta.status_code == 200:
                print("✅ ¡Pago creado exitosamente!")
                return respuesta.json()
            else:
                # Error de Flow
                print(f"❌ Error {respuesta.status_code} de Flow")
                
                try:
                    error_data = respuesta.json()
                    print(f"   Código: {error_data.get('code')}")
                    print(f"   Mensaje: {error_data.get('message')}")
                    
                    return {
                        'error': True,
                        'status_code': respuesta.status_code,
                        'flow_code': error_data.get('code'),
                        'flow_message': error_data.get('message'),
                        'detalle': error_data
                    }
                except:
                    return {
                        'error': True,
                        'status_code': respuesta.status_code,
                        'message': respuesta.text
                    }
        
        except requests.exceptions.Timeout:
            print("❌ Timeout al conectar con Flow")
            return {
                'error': True,
                'message': 'Timeout al conectar con Flow. Intenta nuevamente.'
            }
        
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return {
                'error': True,
                'message': f'Error de conexión: {str(e)}'
            }
    
    def obtener_estado_pago(self, token):
        """
        Obtiene el estado de un pago existente.
        
        Args:
            token (str): Token del pago retornado por Flow
        
        Returns:
            dict: Estado del pago o error
        """
        timestamp = str(int(time.time()))
        
        params = {
            'apiKey': self.api_key,
            'token': token,
            'timestamp': timestamp
        }
        
        # Generar firma
        params['s'] = self._generar_firma(params)
        
        # Construir URL
        partes_url = []
        for clave, valor in params.items():
            if clave == 's':
                partes_url.append(f"{clave}={valor}")
            else:
                valor_codificado = urllib.parse.quote_plus(str(valor))
                partes_url.append(f"{clave}={valor_codificado}")
        
        query_string = '&'.join(partes_url)
        url_completa = f"{self.base_url}/payment/getStatus?{query_string}"
        
        try:
            respuesta = requests.get(url_completa, timeout=30)
            
            if respuesta.status_code == 200:
                return respuesta.json()
            else:
                try:
                    return {
                        'error': True,
                        'data': respuesta.json()
                    }
                except:
                    return {
                        'error': True,
                        'message': respuesta.text
                    }
        
        except Exception as e:
            return {
                'error': True,
                'message': str(e)
            }