from django.shortcuts import render, redirect
from .models import Participacion, Evidencia
from principal.models import PlanMembresia

def participar(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        descripcion = request.POST.get('descripcion')

        participacion = Participacion.objects.create(
            correo=correo,
            telefono=telefono,
            descripcion=descripcion
        )

        planes = PlanMembresia.objects.filter(activo=True).order_by('precio')
        return render(request, 'prueba.html', {
            'mensaje': f'✅ ¡Registro exitoso! Tu código es: <strong>{participacion.codigo}</strong>',
            'mostrar_codigo': True,
            'codigo': participacion.codigo,
            'planes': planes,
        })

    return redirect('home')

def subir_evidencia(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        archivo = request.FILES.get('archivo')

        try:
            participacion = Participacion.objects.get(codigo=codigo)
            Evidencia.objects.create(
                participacion=participacion,
                archivo=archivo
            )

            return render(request, 'subir_evidencia.html', {
                'mensaje': 'Evidencia enviada correctamente ✅'
            })

        except Participacion.DoesNotExist:
            return render(request, 'subir_evidencia.html', {
                'mensaje': 'Código de participación no encontrado ❌'
            })
    
    # IMPORTANTE: Cuando accedes por GET, debe mostrar el formulario
    return render(request, 'subir_evidencia.html')