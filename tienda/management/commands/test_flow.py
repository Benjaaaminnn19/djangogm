from django.core.management.base import BaseCommand
from tienda.flow_service import FlowService
import time

class Command(BaseCommand):
    help = 'Prueba la conexión con Flow'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.WARNING("🧪 PRUEBA DE INTEGRACIÓN CON FLOW"))
        self.stdout.write("=" * 80)
        
        try:
            # Inicializar servicio
            self.stdout.write("\n1️⃣ Inicializando FlowService...")
            flow = FlowService()
            
            # Preparar datos de prueba
            self.stdout.write("\n2️⃣ Preparando orden de prueba...")
            datos_prueba = {
                'commerceOrder': f'TEST-{int(time.time())}',
                'subject': 'Prueba de integración Gimnasio Leblon',
                'amount': 1000,  # $1.000 CLP
                'email': 'test@gimnasioleblon.cl',
                'urlConfirmation': 'https://httpbin.org/post',  # URL de prueba
                'urlReturn': 'https://httpbin.org/get',
                'optional': 'Prueba desde comando Django'
            }
            
            self.stdout.write(f"   Orden: {datos_prueba['commerceOrder']}")
            self.stdout.write(f"   Monto: ${datos_prueba['amount']}")
            
            # Crear pago
            self.stdout.write("\n3️⃣ Creando pago en Flow...")
            resultado = flow.crear_pago(datos_prueba)
            
            # Mostrar resultado
            self.stdout.write("\n4️⃣ Resultado:")
            self.stdout.write("=" * 80)
            
            if 'error' in resultado and resultado['error']:
                # Error
                self.stdout.write(self.style.ERROR("❌ ERROR AL CREAR PAGO"))
                self.stdout.write(f"\nCódigo de estado: {resultado.get('status_code', 'N/A')}")
                self.stdout.write(f"Código Flow: {resultado.get('flow_code', 'N/A')}")
                self.stdout.write(f"Mensaje Flow: {resultado.get('flow_message', 'N/A')}")
                self.stdout.write(f"\nDetalle completo: {resultado}")
                
            else:
                # Éxito
                self.stdout.write(self.style.SUCCESS("✅ ¡PAGO CREADO EXITOSAMENTE!"))
                self.stdout.write(f"\n🔗 URL de pago: {resultado.get('url')}")
                self.stdout.write(f"🎫 Token: {resultado.get('token')}")
                self.stdout.write(f"🆔 Flow Order: {resultado.get('flowOrder')}")
                
                self.stdout.write("\n" + "=" * 80)
                self.stdout.write(self.style.SUCCESS(
                    "✅ La integración con Flow está funcionando correctamente"
                ))
                self.stdout.write(
                    "💡 Puedes abrir la URL de pago en tu navegador para completar la prueba"
                )
            
            self.stdout.write("=" * 80)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ ERROR INESPERADO: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())