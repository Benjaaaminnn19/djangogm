# Generated manually

from django.db import migrations, models
from django.utils import timezone


def migrar_datos_fecha(apps, schema_editor):
    SolicitudPlan = apps.get_model('principal', 'SolicitudPlan')
    for solicitud in SolicitudPlan.objects.all():
        if hasattr(solicitud, 'fecha_solicitud') and solicitud.fecha_solicitud:
            solicitud.fecha_compra = solicitud.fecha_solicitud
        else:
            solicitud.fecha_compra = timezone.now()
        solicitud.estado = 'pagado'
        solicitud.activado = True
        solicitud.save()


class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0003_solicitudplan'),
    ]

    operations = [
        # Agregar nuevos campos primero
        migrations.AddField(
            model_name='solicitudplan',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente de Pago'), ('pagado', 'Pagado'), ('activado', 'Activado'), ('cancelado', 'Cancelado')], default='pagado', max_length=20, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='solicitudplan',
            name='activado',
            field=models.BooleanField(default=True, verbose_name='Activado'),
        ),
        migrations.AddField(
            model_name='solicitudplan',
            name='fecha_compra',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Fecha de Compra'),
        ),
        # Migrar datos de fecha_solicitud a fecha_compra
        migrations.RunPython(migrar_datos_fecha, reverse_code=migrations.RunPython.noop),
        # Eliminar campos antiguos
        migrations.RemoveField(
            model_name='solicitudplan',
            name='procesado',
        ),
        migrations.RemoveField(
            model_name='solicitudplan',
            name='fecha_solicitud',
        ),
        # Hacer fecha_compra requerido
        migrations.AlterField(
            model_name='solicitudplan',
            name='fecha_compra',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Compra'),
        ),
        # Actualizar verbose names
        migrations.AlterModelOptions(
            name='solicitudplan',
            options={'ordering': ['-fecha_compra'], 'verbose_name': 'Compra de Plan', 'verbose_name_plural': 'Compras de Planes'},
        ),
    ]

