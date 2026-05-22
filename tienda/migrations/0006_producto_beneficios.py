from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0005_remove_producto_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='beneficios',
            field=models.TextField(blank=True, default='', verbose_name='Beneficios / Para qué sirve'),
        ),
    ]
