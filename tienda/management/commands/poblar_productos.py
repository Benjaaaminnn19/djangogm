"""
Uso:
    python manage.py poblar_productos
    python manage.py poblar_productos --limpiar   # borra todos los productos antes de crear

Qué hace:
  - Lee las imágenes numeradas de media/productos/ (1.webp, 1-desc.webp, etc.)
  - Sube cada imagen a través de Django storage (= Cloudinary en producción)
  - Crea los registros Producto e ImagenProducto en la base de datos
  - No duplica si el producto ya existe (usa nombre como clave)
"""

import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from tienda.models import Producto, ImagenProducto

# ─────────────────────────────────────────────────────────────
# Datos de los 13 productos.  Edita nombres/precios/stock si
# las imágenes no coinciden con el orden real.
# ─────────────────────────────────────────────────────────────
PRODUCTOS = [
    {
        'numero': 1,
        'nombre': 'Whey Blend Strong 900g',
        'descripcion': (
            'Proteína de suero de leche concentrada e hidrolizada de alta calidad. '
            'Fórmula avanzada con 24g de proteína por porción para maximizar la '
            'ganancia muscular y acelerar la recuperación post-entrenamiento.'
        ),
        'beneficios': (
            '• 24g de proteína pura por porción\n'
            '• Absorción rápida ideal para post-entreno\n'
            '• Bajo en grasa y azúcar\n'
            '• Mejora la recuperación y reduce el catabolismo\n'
            '• Disponible en sabor vainilla y chocolate'
        ),
        'precio': 24990,
        'categoria': 'suplementos',
        'stock': 20,
    },
    {
        'numero': 2,
        'nombre': 'Caffeine Anhydrous 300mg',
        'descripcion': (
            'Cafeína anhidra de máxima pureza para un impulso energético inmediato '
            'sin azúcar ni calorías. Aumenta el enfoque, la resistencia y la quema '
            'de grasa durante el entrenamiento.'
        ),
        'beneficios': (
            '• 300mg de cafeína pura por cápsula\n'
            '• Aumenta la energía y el rendimiento deportivo\n'
            '• Mejora el enfoque mental y la concentración\n'
            '• Potencia la quema de grasa como termogénico\n'
            '• Sin azúcares ni calorías adicionales'
        ),
        'precio': 17990,
        'categoria': 'suplementos',
        'stock': 25,
    },
    {
        'numero': 3,
        'nombre': 'Anabolik Mass Strong 3kg',
        'descripcion': (
            'Hipercalórico de alta densidad nutricional formulado para personas con '
            'metabolismo rápido que buscan ganar masa muscular. Cada porción aporta '
            'más de 1.200 kcal con proteínas de calidad y carbohidratos complejos.'
        ),
        'beneficios': (
            '• +1.200 kcal por porción\n'
            '• Alta proporción de carbohidratos complejos para energía sostenida\n'
            '• 40g de proteína por porción\n'
            '• Ideal para ectomorfos y hardgainers\n'
            '• Favorece el aumento de peso y volumen muscular'
        ),
        'precio': 32790,
        'categoria': 'suplementos',
        'stock': 15,
    },
    {
        'numero': 4,
        'nombre': 'Ashwagandha 60 Cápsulas',
        'descripcion': (
            'Extracto estandarizado de ashwagandha (Withania somnifera) para reducir '
            'el estrés y el cortisol, mejorar la resistencia física y potenciar los '
            'niveles naturales de testosterona.'
        ),
        'beneficios': (
            '• Reduce los niveles de cortisol y estrés crónico\n'
            '• Aumenta la resistencia y la energía natural\n'
            '• Apoya los niveles saludables de testosterona\n'
            '• Mejora la calidad del sueño y la recuperación\n'
            '• Adaptógeno natural 100% vegano'
        ),
        'precio': 19000,
        'categoria': 'suplementos',
        'stock': 30,
    },
    {
        'numero': 5,
        'nombre': 'Revex HC 120 Cápsulas',
        'descripcion': (
            'Termogénico de última generación con una combinación de extractos '
            'naturales que acelera el metabolismo, potencia la lipólisis y reduce '
            'el apetito para resultados visibles en menos tiempo.'
        ),
        'beneficios': (
            '• Acelera el metabolismo y la quema de grasa\n'
            '• Reduce el apetito y controla los antojos\n'
            '• Aumenta la energía durante el entrenamiento\n'
            '• Fórmula termogénica de acción prolongada\n'
            '• 120 cápsulas — hasta 60 días de uso'
        ),
        'precio': 39000,
        'categoria': 'suplementos',
        'stock': 18,
    },
    {
        'numero': 6,
        'nombre': 'Turbo Ripper',
        'descripcion': (
            'Quemador de grasa intensivo con cafeína, L-carnitina y extracto de té '
            'verde. Diseñado para definición muscular extrema, mayor energía y '
            'resistencia cardiovascular elevada.'
        ),
        'beneficios': (
            '• Triple acción: quema grasa + energía + definición\n'
            '• L-carnitina para transporte de ácidos grasos\n'
            '• Extracto de té verde antioxidante\n'
            '• Aumenta la temperatura corporal (termogénesis)\n'
            '• Ideal para etapas de corte o definición'
        ),
        'precio': 28000,
        'categoria': 'suplementos',
        'stock': 22,
    },
    {
        'numero': 7,
        'nombre': 'Strong Test',
        'descripcion': (
            'Potenciador natural de testosterona con zinc, magnesio, vitamina B6 y '
            'extractos botánicos clínicamente estudiados. Formulado para hombres '
            'activos que buscan maximizar su rendimiento hormonal y muscular.'
        ),
        'beneficios': (
            '• Potencia la producción natural de testosterona\n'
            '• Mejora la libido, fuerza y energía\n'
            '• Reduce el cortisol y el estrés oxidativo\n'
            '• Favorece la ganancia de masa muscular magra\n'
            '• Fórmula con ZMA + extractos botánicos'
        ),
        'precio': 22990,
        'categoria': 'suplementos',
        'stock': 20,
    },
    {
        'numero': 8,
        'nombre': 'Whey Blend Protein Strongest 2kg',
        'descripcion': (
            'Proteína de suero premium en formato de 2kg con mezcla de concentrado, '
            'aislado e hidrolizado para un perfil aminoacídico completo. Mayor '
            'rendimiento y recuperación en cada entrenamiento.'
        ),
        'beneficios': (
            '• Mezcla de 3 tipos de proteína de suero\n'
            '• 27g de proteína por porción\n'
            '• Perfil completo de aminoácidos esenciales y BCAA\n'
            '• Excelente digestibilidad y absorción\n'
            '• Formato 2kg — hasta 60 porciones'
        ),
        'precio': 49990,
        'categoria': 'suplementos',
        'stock': 12,
    },
    {
        'numero': 9,
        'nombre': 'Strongest Inferno Pre-Entreno',
        'descripcion': (
            'Pre-entreno de alta intensidad con beta-alanina, citrulina malato, '
            'cafeína y arginina. Fórmula diseñada para rendir al máximo desde el '
            'primer set hasta el último.'
        ),
        'beneficios': (
            '• Explosión de energía y concentración mental\n'
            '• Citrulina malato para mayor bombeo muscular\n'
            '• Beta-alanina para retrasar la fatiga\n'
            '• Aumenta la resistencia y el rendimiento\n'
            '• Sin crash ni efecto rebote post-entrenamiento'
        ),
        'precio': 27990,
        'categoria': 'suplementos',
        'stock': 18,
    },
    {
        'numero': 10,
        'nombre': 'Strong Wrist Wrap',
        'descripcion': (
            'Muñequeras de alta resistencia para press de banca, press militar y '
            'ejercicios de empuje. Soporte firme de la articulación de la muñeca '
            'para entrenar más pesado con mayor seguridad.'
        ),
        'beneficios': (
            '• Soporte y estabilización de la muñeca\n'
            '• Permite mayor carga en ejercicios de empuje\n'
            '• Material elástico de alta resistencia\n'
            '• Cierre ajustable tipo velcro\n'
            '• Un par (derecha + izquierda) por compra'
        ),
        'precio': 15990,
        'categoria': 'accesorios',
        'stock': 35,
    },
    {
        'numero': 11,
        'nombre': 'Creatina Monohidratada 1kg',
        'descripcion': (
            'Creatina monohidratada micronizada de máxima pureza. El suplemento '
            'más respaldado científicamente para aumentar la fuerza, la potencia '
            'explosiva y la masa muscular en deportistas de alto rendimiento.'
        ),
        'beneficios': (
            '• Aumenta la fuerza y potencia explosiva\n'
            '• Favorece la ganancia de masa muscular magra\n'
            '• Recarga el ATP muscular más rápido\n'
            '• Micronizada para mejor disolución y absorción\n'
            '• 1kg — hasta 200 porciones de 5g'
        ),
        'precio': 15990,
        'categoria': 'suplementos',
        'stock': 28,
    },
    {
        'numero': 12,
        'nombre': 'Testo Push',
        'descripcion': (
            'Potenciador hormonal avanzado con tribulus terrestris, fenogreco, '
            'maca andina y vitamina D3. Formulado para hombres mayores de 18 años '
            'que buscan optimizar su perfil hormonal de forma natural.'
        ),
        'beneficios': (
            '• Potencia los niveles naturales de testosterona\n'
            '• Tribulus terrestris + maca andina + fenogreco\n'
            '• Mejora la vitalidad, el ánimo y el rendimiento\n'
            '• Aumenta la masa muscular y reduce la grasa\n'
            '• Vitamina D3 para soporte hormonal completo'
        ),
        'precio': 39000,
        'categoria': 'suplementos',
        'stock': 16,
    },
    {
        'numero': 13,
        'nombre': 'BCAA 8:1:1 Strongest',
        'descripcion': (
            'Aminoácidos de cadena ramificada en proporción 8:1:1 (leucina, '
            'isoleucina, valina) para preservar la masa muscular durante el '
            'entrenamiento y acelerar la recuperación.'
        ),
        'beneficios': (
            '• Proporción 8:1:1 con mayor concentración de leucina\n'
            '• Reduce el catabolismo muscular durante el ejercicio\n'
            '• Acelera la síntesis de proteínas musculares\n'
            '• Disminuye el dolor muscular post-entrenamiento\n'
            '• Puede usarse intra o post-entrenamiento'
        ),
        'precio': 18990,
        'categoria': 'suplementos',
        'stock': 24,
    },
]

# Extensiones a probar para la imagen principal y la descriptiva
EXTENSIONES = ['webp', 'png', 'jpg', 'jpeg', 'avif']


def _buscar_archivo(directorio, nombre_base):
    """Devuelve la ruta completa del primer archivo que coincida con nombre_base + alguna extensión."""
    for ext in EXTENSIONES:
        ruta = os.path.join(directorio, f'{nombre_base}.{ext}')
        if os.path.isfile(ruta):
            return ruta
    return None


class Command(BaseCommand):
    help = 'Pobla la tienda con los 13 productos usando imágenes numeradas de media/productos/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los productos existentes antes de crear los nuevos',
        )

    def handle(self, *args, **options):
        media_productos = os.path.join(settings.BASE_DIR, 'media', 'productos')

        if not os.path.isdir(media_productos):
            self.stdout.write(self.style.ERROR(
                f'No existe la carpeta: {media_productos}'
            ))
            return

        if options['limpiar']:
            eliminados, _ = Producto.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Se eliminaron {eliminados} productos existentes.'))

        creados = 0
        omitidos = 0

        for datos in PRODUCTOS:
            numero = datos['numero']

            # Evitar duplicados por nombre
            if Producto.objects.filter(nombre=datos['nombre']).exists():
                self.stdout.write(self.style.WARNING(
                    f'  [OMITIDO] Ya existe: {datos["nombre"]}'
                ))
                omitidos += 1
                continue

            # Crear el producto
            producto = Producto.objects.create(
                nombre=datos['nombre'],
                descripcion=datos['descripcion'],
                beneficios=datos['beneficios'],
                precio=datos['precio'],
                categoria=datos['categoria'],
                stock=datos['stock'],
                activo=True,
            )

            # ── Imagen principal ──────────────────────────────────────────
            ruta_principal = _buscar_archivo(media_productos, str(numero))
            if ruta_principal:
                filename = os.path.basename(ruta_principal)
                with open(ruta_principal, 'rb') as f:
                    imagen_obj = ImagenProducto(
                        producto=producto,
                        orden=0,
                        es_principal=True,
                    )
                    imagen_obj.imagen.save(filename, File(f), save=False)
                    imagen_obj.save()
                self.stdout.write(f'    ✔ Imagen principal: {filename}')
            else:
                self.stdout.write(self.style.WARNING(
                    f'    ✗ No se encontró imagen principal para número {numero}'
                ))

            # ── Imagen descriptiva ────────────────────────────────────────
            ruta_desc = _buscar_archivo(media_productos, f'{numero}-desc')
            if ruta_desc:
                filename_desc = os.path.basename(ruta_desc)
                with open(ruta_desc, 'rb') as f:
                    imagen_desc = ImagenProducto(
                        producto=producto,
                        orden=1,
                        es_principal=False,
                    )
                    imagen_desc.imagen.save(filename_desc, File(f), save=False)
                    imagen_desc.save()
                self.stdout.write(f'    ✔ Imagen descriptiva: {filename_desc}')
            else:
                self.stdout.write(self.style.WARNING(
                    f'    ✗ No se encontró imagen descriptiva para número {numero}'
                ))

            creados += 1
            self.stdout.write(self.style.SUCCESS(f'  [OK] {producto.nombre}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {creados} productos creados, {omitidos} omitidos por duplicado.'
        ))
        self.stdout.write('')
        self.stdout.write('Para exportar y cargar en producción:')
        self.stdout.write('  python manage.py dumpdata tienda.Producto tienda.ImagenProducto '
                          '--indent 2 > tienda/fixtures/productos.json')
        self.stdout.write('  # En Railway:')
        self.stdout.write('  python manage.py loaddata tienda/fixtures/productos.json')
