import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gimnasio.settings')
django.setup()

from django.conf import settings
from tienda.flow_service import FlowService

def test_flow_config():
    """Prueba la configuración de Flow"""
    print("=" * 60)
    print("CONFIGURACIÓN DE FLOW")
    print("=" * 60)
    
    print(f"\n📊 Ambiente actual:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   FLOW_SANDBOX: {settings.FLOW_SANDBOX}")
    
    environment = "sandbox" if settings.FLOW_SANDBOX else "prod"
    print(f"\n🔧 Usando ambiente: {environment}")
    
    print(f"\n🔑 Credenciales {environment}:")
    if environment == "sandbox":
        print(f"   API Key: {settings.FLOW_SANDBOX_API_KEY[:20]}...")
        print(f"   Secret Key: {settings.FLOW_SANDBOX_SECRET_KEY[:20]}...")
    else:
        if settings.FLOW_PROD_API_KEY:
            print(f"   API Key: {settings.FLOW_PROD_API_KEY[:20]}...")
            print(f"   Secret Key: {settings.FLOW_PROD_SECRET_KEY[:20]}...")
        else:
            print("   ⚠️  NO HAY CREDENCIALES DE PRODUCCIÓN")
    
    print(f"\n🌐 URLs:")
    print(f"   Base URL: {FlowService(environment).base_url}")
    
    print("\n" + "=" * 60)
    print("✅ Configuración verificada")
    print("=" * 60)

if __name__ == "__main__":
    test_flow_config()