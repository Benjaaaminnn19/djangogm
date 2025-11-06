from django.core.management.base import BaseCommand
from principal.models import Clase
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Crea clases de ejemplo para el gimnasio'

    def handle(self, *args, **options):
        # Obtener la fecha de mañana a las 18:00
        fecha_base = timezone.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        clases_ejemplo = [
            {
                'nombre': 'Clases Dirigidas',
                'fecha': fecha_base,
                'cupos': 10
            },
            {
                'nombre': 'Spinning',
                'fecha': fecha_base + timedelta(days=1),
                'cupos': 15
            },
            {
                'nombre': 'Evaluación Corporal',
                'fecha': fecha_base + timedelta(days=2),
                'cupos': 5
            },
            {
                'nombre': 'Rutinas Personalizadas',
                'fecha': fecha_base + timedelta(days=3),
                'cupos': 8
            },
            {
                'nombre': 'Clases Dirigidas',
                'fecha': fecha_base + timedelta(days=4, hours=6),  # 6:00 AM
                'cupos': 12
            },
            {
                'nombre': 'Spinning',
                'fecha': fecha_base + timedelta(days=5),
                'cupos': 20
            },
        ]
        
        creadas = 0
        for clase_data in clases_ejemplo:
            clase, created = Clase.objects.get_or_create(
                nombre=clase_data['nombre'],
                fecha=clase_data['fecha'],
                defaults={'cupos': clase_data['cupos']}
            )
            if created:
                creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Clase creada: {clase.nombre} - {clase.fecha.strftime("%d/%m/%Y %H:%M")} - {clase.cupos} cupos'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Clase ya existe: {clase.nombre} - {clase.fecha.strftime("%d/%m/%Y %H:%M")}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado. {creadas} clase(s) nueva(s) creada(s).'
            )
        )

