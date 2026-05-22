from django.contrib import admin
from .models import Lead
from .models import Clase, Reserva, SolicitudPlan
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Miembro, Asistencia
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'fecha_registro', 'activo']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'email']
    readonly_fields = ['fecha_registro']
    list_editable = ['activo']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-fecha_registro')

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'cupos', 'cupos_disponibles')
    list_filter = ('fecha',)
    search_fields = ('nombre',)
    date_hierarchy = 'fecha'
    list_editable = ('cupos',)  # Permite editar cupos directamente desde la lista
    
    fieldsets = (
        ('Información de la Clase', {
            'fields': ('nombre',)
        }),
        ('Fecha y Cupos', {
            'fields': ('fecha', 'cupos'),
            'description': 'Selecciona una fecha y hora futura para que la clase aparezca en la lista disponible.'
        }),
    )
    
    def cupos_disponibles(self, obj):
        reservas = Reserva.objects.filter(clase=obj).count()
        disponibles = obj.cupos - reservas
        if disponibles <= 0:
            return f"0 (Agotado)"
        return f"{disponibles} de {obj.cupos}"
    cupos_disponibles.short_description = 'Cupos Disponibles'

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clase', 'correo', 'aprobado', 'fecha_reserva')
    list_filter = ('aprobado', 'fecha_reserva', 'clase')
    search_fields = ('nombre', 'correo', 'clase__nombre')
    readonly_fields = ('fecha_reserva',)
    date_hierarchy = 'fecha_reserva'
    list_editable = ('aprobado',)  # Permite aprobar directamente desde la lista
    # Los correos de confirmación/cancelación se envían via signals (principal/signals.py),
    # lo que garantiza que funcionen sin importar desde dónde se cambie el estado.

class MiembroCreationForm(UserCreationForm):
    class Meta:
        model = Miembro
        fields = ('email', 'telefono', 'nombre')

class MiembroChangeForm(UserChangeForm):
    class Meta:
        model = Miembro
        fields = '__all__'

@admin.register(Miembro)
class MiembroAdmin(BaseUserAdmin):
    form = MiembroChangeForm
    add_form = MiembroCreationForm
    
    list_display = ('email', 'telefono', 'nombre', 'is_active', 'fecha_inicio', 'activo')
    list_filter = ('activo', 'is_staff', 'is_superuser', 'fecha_inicio')
    search_fields = ('email', 'telefono', 'nombre')
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {'fields': ('email', 'telefono', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'fecha_inicio', 'activo')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'telefono', 'nombre', 'password1', 'password2', 'activo'),
        }),
    )

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'fecha_entrada')
    list_filter = ('fecha_entrada',)
    search_fields = ('miembro__nombre', 'miembro__email', 'miembro__telefono')
    readonly_fields = ('miembro', 'fecha_entrada')
    ordering = ('-fecha_entrada',)