# diagnostic_fixed.py
import hmac
import hashlib
import time
import urllib.parse

# TUS CREDENCIALES REALES
API_KEY = "7493302F-8AF1-4D67-AF77-940CA7BC6L4F"
SECRET_KEY = "Oeabd73cb54bc64196709d8298bf9f6ed62efda0"

# Parámetros de ejemplo (igual que tu petición)
params = {
    'apiKey': API_KEY,
    'commerceOrder': 'ORD-C1A0A9F1',
    'subject': 'Compra en Gimnasio Leblon - ORD-C1A0A9F1',
    'currency': 'CLP',
    'amount': '27900',
    'email': 'benjamin@example.com',
    'urlConfirmation': 'https://tudominio.com/confirmacion/',
    'urlReturn': 'https://tudominio.com/retorno/',
    'timestamp': str(int(time.time()))
}

print("=== DIAGNÓSTICO FLOW CORREGIDO ===")

# 1. Mostrar parámetros originales
print("\n1. Parámetros originales:")
for k, v in sorted(params.items()):
    print(f"   {k}: '{v}'")

# 2. Crear string para firma CON URL ENCODING
sorted_params = sorted(params.items())
string_to_sign = '&'.join([
    f"{k}={urllib.parse.quote(str(v), safe='')}" 
    for k, v in sorted_params
])

print(f"\n2. String para firmar (CON encoding):")
print(f"'{string_to_sign}'")

# 3. Calcular firma
signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    string_to_sign.encode('utf-8'),
    hashlib.sha256
).hexdigest().upper()

print(f"\n3. Firma calculada:")
print(f"{signature}")

# 4. Crear URL final (con encoding para URL)
params_with_signature = params.copy()
params_with_signature['s'] = signature

encoded_url_params = []
for k, v in params_with_signature.items():
    if k == 's':
        encoded_url_params.append(f"{k}={v}")
    else:
        encoded_url_params.append(f"{k}={urllib.parse.quote_plus(str(v))}")

query_string = '&'.join(encoded_url_params)
final_url = f"https://www.flow.cl/api/payment/create?{query_string}"

print(f"\n4. URL final (segura - sin secret):")
safe_url = final_url.replace(SECRET_KEY, '***SECRET***')
print(safe_url)

# 5. Comparar con tu error anterior
print(f"\n5. Diferencia clave:")
print(f"   Anterior (sin encoding): 'Compra en Gimnasio...'")
print(f"   Correcto (con encoding): '{urllib.parse.quote('Compra en Gimnasio Leblon - ORD-C1A0A9F1', safe='')}'")