import hmac
import hashlib
import requests
import time
import urllib.parse
from django.conf import settings

class FlowService:
    """
    Servicio Flow para pagos - Versión ultra-robusta
    Corrige problemas comunes de firma inválida
    """
    
    def __init__(self):
        # Obtener y limpiar credenciales (eliminar espacios en blanco)
        self.api_key = getattr(settings, 'FLOW_API_KEY', '').strip()
        self.secret_key = getattr(settings, 'FLOW_SECRET_KEY', '').strip()
        self.base_url = getattr(settings, 'FLOW_API_URL', 'https://sandbox.flow.cl/api').strip()
        
        # Asegurar que la URL no termine con /
        self.base_url = self.base_url.rstrip('/')
        
        # Validar
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "❌ Credenciales de Flow no configuradas. "
                "Verifica FLOW_API_KEY y FLOW_SECRET_KEY"
            )
        
        print(f"✅ FlowService inicializado")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"   Secret Key: {self.secret_key[:8]}...{self.secret_key[-4:]}")
    
    def _generar_firma(self, params):
        """
        Genera firma HMAC-SHA256 siguiendo EXACTAMENTE la especificación de Flow
        
        IMPORTANTE: Flow requiere:
        1. Excluir el parámetro 's'
        2. Ordenar alfabéticamente por clave
        3. URL encode cada valor (excepto la firma)
        4. Concatenar como: key1=value1&key2=value2
        5. Calcular HMAC-SHA256 con secret_key
        6. Convertir a UPPERCASE hexadecimal
        """
        # 1. Remover 's' si existe
        params_limpios = {k: v for k, v in params.items() if k != 's'}
        
        # 2. Ordenar alfabéticamente
        params_ordenados = sorted(params_limpios.items())
        
        # 3. Construir string con URL encoding estricto
        partes = []
        for clave, valor in params_ordenados:
            # Convertir a string
            valor_str = str(valor)
            
            # URL encode con safe='' para codificar TODO
            # Esto convierte espacios a %20, caracteres especiales, etc.
            valor_codificado = urllib.parse.quote(valor_str, safe='')
            
            partes.append(f"{clave}={valor_codificado}")
        
        # Unir con &
        string_a_firmar = '&'.join(partes)
        
        if settings.DEBUG:
            print(f"\n{'='*80}")
            print("🔐 GENERACIÓN DE FIRMA:")
            print(f"{'='*80}")
            print(f"String a firmar:")
            print(f"{string_a_firmar}")
            print(f"\nSecret Key: {self.secret_key[:8]}...{self.secret_key[-4:]}")
        
        # 4. Calcular HMAC-SHA256
        firma = hmac.new(
            self.secret_key.encode('utf-8'),
            string_a_firmar.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()  # ← UPPERCASE es importante
        
        if settings.DEBUG:
            print(f"Firma generada: {firma}")
            print(f"{'='*80}\n")
        
        return firma
    
    def crear_pago(self, datos_orden):
        """
        Crea un pago en Flow
        
        Args:
            datos_orden (dict): {
                'commerceOrder': str,  # ID único
                'subject': str,        # Descripción
                'amount': int,         # Monto en CLP
                'email': str,          # Email del pagador
                'urlConfirmation': str, # Webhook
                'urlReturn': str       # Retorno usuario
            }
        
        Returns:
            dict: {'url': str, 'token': str, 'flowOrder': int}
                  o {'error': True, 'message': str}
        """
        # Validar campos obligatorios
        campos_requeridos = [
            'commerceOrder', 'subject', 'amount', 
            'email', 'urlConfirmation', 'urlReturn'
        ]
        
        for campo in campos_requeridos:
            if campo not in datos_orden or not datos_orden[campo]:
                return {
                    'error': True,
                    'message': f'Falta campo requerido: {campo}'
                }
        
        # Timestamp actual
        timestamp = str(int(time.time()))
        
        # Construir parámetros en el ORDEN EXACTO que requiere Flow
        # IMPORTANTE: El orden alfabético se hace después, esto es solo para claridad
        params = {
            'apiKey': self.api_key,
            'commerceOrder': str(datos_orden['commerceOrder']),
            'subject': str(datos_orden['subject']),
            'currency': 'CLP',
            'amount': str(int(datos_orden['amount'])),  # Asegurar que sea entero
            'email': str(datos_orden['email']),
            'urlConfirmation': str(datos_orden['urlConfirmation']),
            'urlReturn': str(datos_orden['urlReturn']),
            'timestamp': timestamp
        }
        
        # Agregar optional si existe
        if 'optional' in datos_orden and datos_orden['optional']:
            params['optional'] = str(datos_orden['optional'])
        
        # Generar firma
        params['s'] = self._generar_firma(params)
        
        # Construir URL para GET request
        # IMPORTANTE: Para la URL, usar quote_plus (espacios → +)
        partes_url = []
        for clave, valor in params.items():
            if clave == 's':
                # La firma NO se codifica
                partes_url.append(f"{clave}={valor}")
            else:
                # Otros valores: codificar para URL (espacios → +)
                valor_codificado = urllib.parse.quote_plus(str(valor))
                partes_url.append(f"{clave}={valor_codificado}")
        
        query_string = '&'.join(partes_url)
        url_completa = f"{self.base_url}/payment/create?{query_string}"
        
        if settings.DEBUG:
            print(f"\n{'='*80}")
            print("📤 PETICIÓN A FLOW:")
            print(f"{'='*80}")
            print(f"Método: GET")
            print(f"URL: {url_completa[:150]}...")
            print(f"{'='*80}\n")
        
        # Hacer petición GET
        try:
            print("📤 Enviando petición...")
            respuesta = requests.get(url_completa, timeout=30)
            
            print(f"📥 Respuesta: {respuesta.status_code}")
            
            if respuesta.status_code == 200:
                print("✅ ¡Pago creado exitosamente!")
                return respuesta.json()
            
            else:
                # Error de Flow
                print(f"❌ Error {respuesta.status_code}")
                
                try:
                    error_data = respuesta.json()
                    print(f"   Código Flow: {error_data.get('code')}")
                    print(f"   Mensaje Flow: {error_data.get('message')}")
                    
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
                        'message': respuesta.text[:500]
                    }
        
        except requests.exceptions.Timeout:
            return {
                'error': True,
                'message': 'Timeout al conectar con Flow'
            }
        
        except Exception as e:
            return {
                'error': True,
                'message': f'Error de conexión: {str(e)}'
            }
    
    def obtener_estado_pago(self, token):
        """
        Obtiene el estado de un pago
        
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
                    return {'error': True, 'data': respuesta.json()}
                except:
                    return {'error': True, 'message': respuesta.text[:500]}
        
        except Exception as e:
            return {'error': True, 'message': str(e)}