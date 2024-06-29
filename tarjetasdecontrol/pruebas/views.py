from io import BytesIO
from django.db import transaction
from django.http import HttpResponse
from .signals import update_tarjeta_fields
from .utils import obtener_datos_api, recalculate_task_start_times
from .models import NewTarjeta, NewOrden, NewTarea
from .forms import NewTareaForm, NewTarjetaForm, IncidentForm
from django.urls import reverse
from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from openpyxl import Workbook

def lista_tarjetas(request, pk):
    if request.method == "POST":
        relacion_id = request.POST.get("relacion_id")
        estado = request.POST.get("estado")

        relacion = get_object_or_404(NewOrden, pk=relacion_id, tarjeta__usuario=request.user)

        if estado in dict(NewOrden.ESTADO_CHOICES).keys():
            with transaction.atomic():
                relacion.estado = estado
                relacion.save()

        return redirect('lista_tarjetas', pk=relacion.tarjeta.id)

    tarjeta = get_object_or_404(NewTarjeta.objects.prefetch_related(
        'tareas__neworden_set', 'incidents'
    ).select_related('usuario'), pk=pk, usuario=request.user)
    tarjetas = [tarjeta]

    tareas_con_hora = recalculate_task_start_times(tarjeta)
    for tarea_info in tareas_con_hora:
        relacion = tarea_info['tarea'].neworden_set.filter(tarjeta=tarjeta).first()
        tarea_info.update({
            'relacion_id': relacion.id if relacion else None,
            'estado': relacion.estado if relacion else ''
        })

    tarjeta.tareas_con_hora = tareas_con_hora
    tarjeta.incidents_list = tarjeta.incidents.all()

    return render(request, 'pruebas/lista_tarjetas.html', {
        'tarjetas': tarjetas,
        'porcentaje_completado': tarjeta.porcentaje_completado,
        'porcentaje_incidentes': tarjeta.porcentaje_incidentes,
        'valorizacion': tarjeta.valorizacion
    })

def cambiar_orden(request, tarjeta_id, tarea_id, nuevo_orden):
    tarjeta = get_object_or_404(NewTarjeta, pk=tarjeta_id)
    relacion = get_object_or_404(NewOrden, tarjeta=tarjeta, tarea_id=tarea_id)
    relaciones = NewOrden.objects.filter(tarjeta=tarjeta).order_by('order')
    max_orden = relaciones.count()
    
    if nuevo_orden < 1:
        nuevo_orden = 1
    elif nuevo_orden > max_orden:
        nuevo_orden = max_orden

    current_order = relacion.order

    if nuevo_orden != current_order:
        if nuevo_orden < current_order:
            relaciones.filter(order__gte=nuevo_orden, order__lt=current_order).update(order=models.F('order') + 1)
        elif nuevo_orden > current_order:
            relaciones.filter(order__gt=current_order, order__lte=nuevo_orden).update(order=models.F('order') - 1)

        relacion.order = nuevo_orden
        relacion.save()

    recalculate_task_start_times(tarjeta)
    return redirect('lista_tarjetas', pk=tarjeta_id)

def descargar_excel(request, pk):
    tarjeta = get_object_or_404(NewTarjeta.objects.prefetch_related(
        'tareas__neworden_set', 'incidents'
    ).select_related('usuario'), pk=pk)

    tareas_con_hora = recalculate_task_start_times(tarjeta)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tarjeta de Control"

    # Agregar encabezados
    ws.append(["Verbo", "Objeto", "Orden de Venta", "Cliente", "Inicio", "Fin", "Estado"])

    # Agregar datos
    for tarea_info in tareas_con_hora:
        ws.append([
            tarea_info['tarea'].verbo,
            tarea_info['tarea'].objeto,
            tarea_info['tarea'].orden_venta,
            tarea_info['tarea'].cliente,
            tarea_info['calculated_start_time'].strftime("%H:%M"),
            tarea_info['end_time'].strftime("%H:%M"),
        ])

    # Agregar tabla de incidentes
    ws2 = wb.create_sheet(title="Incidentes")
    ws2.append(["Descripción", "Duración (minutos)"])
    for incident in tarjeta.incidents.all():
        ws2.append([incident.descripcion, incident.duracion])

    # Guardar en un archivo virtual y crear la respuesta
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Tarjeta_{tarjeta.usuario.username}_{tarjeta.fecha}.xlsx'
    return response

@login_required
def new_lista_tareas(request):
    cache_key = f'tareas_{request.user.id}'
    tareas = cache.get(cache_key)
    if not tareas:
        tareas = NewTarea.objects.filter(usuario=request.user).order_by('-id')
        cache.set(cache_key, tareas, timeout=300)
    return render(request, 'tareas/new_lista_tareas.html', {'tareas': tareas})

@login_required
def new_nueva_tarea(request):
    ordenes = obtener_datos_api()
    tareas = NewTarea.objects.filter(usuario=request.user).order_by('-id')
    
    if request.method == "POST":
        form = NewTareaForm(request.POST, ordenes=ordenes)
        if form.is_valid():
            nueva_tarea = form.save(commit=False)
            nueva_tarea.usuario = request.user
            nueva_tarea.cliente = form.cleaned_data['cliente']  # Asigna el cliente aquí
            nueva_tarea.save()
            if 'save_and_add_another' in request.POST:
                return redirect('new_nueva_tarea')
            return redirect('new_lista_tareas')
    else:
        form = NewTareaForm(ordenes=ordenes)

    context = {
        'form': form,
        'tareas': tareas
    }
    
    return render(request, 'tareas/nueva_tarea.html', context)

@login_required
def new_editar_tarea(request, pk):
    ordenes = obtener_datos_api()
    tarea = get_object_or_404(NewTarea, pk=pk)

    if request.method == "POST":
        form = NewTareaForm(request.POST, ordenes=ordenes, instance=tarea)
        if form.is_valid():
            form.save()
            cache.delete(f'tareas_{request.user.id}')
            return redirect('new_lista_tareas')
    else:
        form = NewTareaForm(ordenes=ordenes, instance=tarea)
    
    return render(request, 'tareas/editar_tarea.html', {'form': form})

@login_required
def new_eliminar_tarea(request, pk):
    tarea = get_object_or_404(NewTarea, pk=pk)

    if request.method == "POST":
        tarea.delete()
        cache.delete(f'tareas_{request.user.id}')
        return redirect('new_lista_tareas')
    
    return render(request, 'tareas/eliminar_tarea.html', {'tarea': tarea})



@login_required
def new_lista_tarjetas(request):
    cache_key = f'tarjetas_{request.user.id}'
    tarjetas = cache.get(cache_key)
    if not tarjetas:
        tarjetas = NewTarjeta.objects.filter(usuario=request.user).order_by('-id')
        cache.set(cache_key, tarjetas, timeout=300)  # Cache por 5 minutos
    return render(request, 'tarjetas/new_lista_tarjetas.html', {'tarjetas': tarjetas})

    # # Filtrar las tareas incompletas y reprogramadas del usuario actual
    # tareas_incompletas = NewTarea.objects.filter(
    #     neworden__estado='incompleta',
    #     neworden__tarjeta__usuario=request.user
    # ).distinct()
    
    # tareas_reprogramadas = NewTarea.objects.filter(
    #     neworden__estado='reprogramada',
    #     neworden__tarjeta__usuario=request.user
    # ).distinct()
@login_required
def new_nueva_tarjeta(request):
    if request.method == "POST":
        form = NewTarjetaForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                tarjeta = form.save(commit=False)
                tarjeta.usuario = request.user
                tarjeta.save()
                
                # Obtener el orden de las tareas
                orden_tareas = request.POST.get('orden_tareas', '')
                tarea_ids = orden_tareas.split(',')
                
                # Crear las relaciones NewOrden con el orden correcto
                for order, tarea_id in enumerate(tarea_ids, start=1):
                    tarea = NewTarea.objects.get(id=tarea_id)
                    NewOrden.objects.create(tarjeta=tarjeta, tarea=tarea, order=order)
                
                update_tarjeta_fields(tarjeta)
                cache.delete(f'tarjetas_{request.user.id}')
                return redirect(reverse('lista_tarjetas', kwargs={'pk': tarjeta.pk}))
    else:
        form = NewTarjetaForm(user=request.user)
    
    context = {
        'form': form
    }
    
    return render(request, 'tarjetas/nueva_tarjeta.html', context)





@login_required
def new_editar_tarjeta(request, pk):
    tarjeta = get_object_or_404(NewTarjeta, pk=pk, usuario=request.user)
    if request.method == "POST":
        form = NewTarjetaForm(request.POST, instance=tarjeta, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                tarjeta = form.save(commit=False)
                tarjeta.usuario = request.user
                tarjeta.save()
                nuevas_tareas = form.cleaned_data['tareas']
                tarjeta.tareas.clear()
                ordenes = [NewOrden(tarjeta=tarjeta, tarea=tarea, order=order) for order, tarea in enumerate(nuevas_tareas, start=1)]
                NewOrden.objects.bulk_create(ordenes)
                update_tarjeta_fields(tarjeta) 
                cache.delete(f'tarjetas_{request.user.id}')
                return redirect(reverse('new_lista_tarjetas'))
    else:
        form = NewTarjetaForm(instance=tarjeta, user=request.user)
    return render(request, 'tarjetas/editar_tarjeta.html', {'form': form})

@login_required
def new_eliminar_tarjeta(request, pk):
    tarjeta = get_object_or_404(NewTarjeta, pk=pk, usuario=request.user)
    if request.method == "POST":
        tarjeta.delete()
        cache.delete(f'tarjetas_{request.user.id}')
        return redirect('new_lista_tarjetas')
    return render(request, 'tarjetas/eliminar_tarjeta.html', {'tarjeta': tarjeta})

@login_required
def create_incident(request, tarjeta_id):
    tarjeta = get_object_or_404(NewTarjeta, id=tarjeta_id)

    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                incident = form.save(commit=False)
                incident.tarjeta = tarjeta
                incident.save()
                
                # Invalida la caché si es necesario
                cache.delete(f'tarjetas_{request.user.id}')
                
                if 'save_and_add_another' in request.POST:
                    return redirect('create_incident', tarjeta_id=tarjeta_id)
                return redirect('new_lista_tarjetas')
    else:
        form = IncidentForm()

    return render(request, 'create_incident.html', {'form': form, 'tarjeta': tarjeta})
