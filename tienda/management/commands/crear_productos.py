from django.core.management.base import BaseCommand
from django.core.files import File
import os
from tienda.models import Producto

class Command(BaseCommand):
    help = 'Crea productos de prueba para la tienda'

    def handle(self, *args, **options):
        productos_data = [
            {
                'nombre': 'Proteína Whey Gold Standard',
                'descripcion': 'Proteína de suero de leche de alta calidad para maximizar tus resultados. Ideal para post-entrenamiento.',
                'precio': 45000,
                'categoria': 'suplementos',
                'stock': 50,
                'imagen': 'On-Creatina-Monohidratada-300gr-1-86590.webp'
            },
            {
                'nombre': 'Creatina Monohidratada',
                'descripcion': 'Creatina pura para aumentar la fuerza y masa muscular. Suplemento esencial para cualquier deportista.',
                'precio': 25000,
                'categoria': 'suplementos',
                'stock': 30,
                'imagen': 'On-Creatina-Monohidratada-300gr-1-86590.webp'
            },
            {
                'nombre': 'Camiseta Deportiva Premium',
                'descripcion': 'Camiseta transpirable y cómoda para tus entrenamientos. Tecnología de secado rápido.',
                'precio': 15000,
                'categoria': 'ropa',
                'stock': 100,
                'imagen': 'encuentrame-diseno-camiseta-gym-camiseta-vectorial-gym_812921-73.avif'
            },
            {
                'nombre': 'Guantes de Gimnasio',
                'descripcion': 'Guantes profesionales para levantamiento de pesas. Protección y agarre superior.',
                'precio': 12000,
                'categoria': 'accesorios',
                'stock': 75,
                'imagen': 'logo.jpg'
            },
            {
                'nombre': 'Proteína Whey Chocolate',
                'descripcion': 'Deliciosa proteína de chocolate para recuperación muscular. Sabor premium y fácil digestión.',
                'precio': 48000,
                'categoria': 'suplementos',
                'stock': 40,
                'imagen': 'Prote+na+whey+OPTIMUN+NUTRITION+Gold+Standard+chocolate+908+g.jpg'
            },
            {
                'nombre': 'Short Deportivo',
                'descripcion': 'Short cómodo y elástico para cualquier actividad deportiva. Diseño moderno y funcional.',
                'precio': 18000,
                'categoria': 'ropa',
                'stock': 80,
                'imagen': 'encuentrame-diseno-camiseta-gym-camiseta-vectorial-gym_812921-73.avif'
            }
        ]

        for producto_data in productos_data:
            # Crear el producto
            producto = Producto.objects.create(
                nombre=producto_data['nombre'],
                descripcion=producto_data['descripcion'],
                precio=producto_data['precio'],
                categoria=producto_data['categoria'],
                stock=producto_data['stock']
            )

            # Asignar imagen si existe
            imagen_path = os.path.join('media', 'productos', producto_data['imagen'])
            if os.path.exists(imagen_path):
                with open(imagen_path, 'rb') as f:
                    producto.imagen.save(
                        producto_data['imagen'],
                        File(f),
                        save=True
                    )

            self.stdout.write(
                self.style.SUCCESS(f'Producto creado: {producto.nombre}')
            )

        self.stdout.write(
            self.style.SUCCESS('¡Productos de prueba creados exitosamente!')
        )
