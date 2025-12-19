import hmac
import hashlib
import urllib.parse

# TUS CREDENCIALES DE SANDBOX (cópialas de Flow)
API_KEY = "346F180A-05F3-4C5A-8846-20LEBCB5EF2B"  # ← Pega tu API Key real
SECRET_KEY = "77e5d39b6c036c35e6c37005bc73f9f939530ec3"  # ← Pega tu Secret Key real

# Parámetros de prueba mínimos
params = {
    'apiKey': API_KEY,
    'commerceOrder': 'TEST-001',
    'subject': 'Test',
    'currency': 'CLP',
    'amount': '1000',
    'email': 'test@test.com',
    'urlConfirmation': 'https://httpbin.org/post',
    'urlReturn': 'https://httpbin.org/get',
    'timestamp': '1234567890'
}

# Ordenar alfabéticamente
params_ordenados = sorted(params.items())

# Construir string
partes = []
for clave, valor in params_ordenados:
    valor_codificado = urllib.parse.quote(str(valor), safe='')
    partes.append(f"{clave}={valor_codificado}")

string_a_firmar = '&'.join(partes)

print("String a firmar:")
print(string_a_firmar)
print()

# Calcular firma
firma = hmac.new(
    SECRET_KEY.encode('utf-8'),
    string_a_firmar.encode('utf-8'),
    hashlib.sha256
).hexdigest().upper()

print("Firma generada:")
print(firma)