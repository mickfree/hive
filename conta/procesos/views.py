from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

import logging

from procesos.forms import ProcesoForm, SubprocesoForm, ProcesoEditForm, SubprocesoEditForm, TareaPruebaForm

from procesos.models import Proceso, Subproceso
from tareas.models import Tarea


#
#   PROCESOS
#
# ver procesos creados
def lista_procesos(request):
    procesos = Proceso.objects.all()
    return render(request, 'procesos/lista_procesos.html', {'procesos': procesos})

def ver_proceso(request, proceso_id):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    subprocesos = proceso.subprocesos.all()  # Ajusta esto según tu modelo

    return render(request, 'procesos/ver_proceso.html', {
        'proceso': proceso,
        'subprocesos': subprocesos
    })

def crear_proceso(request):
    if request.method == 'POST':
        form = ProcesosForm(request.POST)
        if form.is_valid():
            proceso = form.save(commit=False)
            proceso.save()  # Guarda el Proceso para obtener un ID.

            # Ahora establece explícitamente las relaciones ManyToMany.
            # Asegúrate de que 'subprocesos' es el nombre correcto del campo en tu formulario.
            proceso.subprocesos.set(form.cleaned_data['subprocesos'])

            return redirect('lista_procesos')
    else:
        form = ProcesosForm()

    return render(request, 'procesos/crear_proceso.html', {'form': form})

def eliminar_proceso(request, proceso_id):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    if request.method == 'POST':
        # Delete subprocess
        for subproceso in proceso.subprocesos.all() :
            for tarea in subproceso.tareas.all() :
                tarea.delete()
            subproceso.delete()
        proceso.delete()
        return HttpResponse('')  # Respuesta vacía para HTMX
        # TODO: Render only the table
    else:
        return redirect('lista_procesos')

def editar_proceso(request, proceso_id):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    if request.method == 'POST':
        form = ProcesoEditForm(request.POST, instance=proceso)
        if form.is_valid():
            proceso = form.save()
#            proceso.subprocesos.set(form.cleaned_data['subprocesos'])
#            proceso.tareas.set(form.cleaned_data['tareas'])
            return redirect('lista_procesos')
    else:
        form = ProcesoEditForm(instance=proceso)

    return render(request, 'procesos/editar_proceso.html', {'form': form})

#
#   SUBPROCESOS
#
def lista_subprocesos(request):
    subprocesos = Subproceso.objects.all()
    return render(request, 'subprocesos/lista_subprocesos.html', {'subprocesos': subprocesos})

def ver_subproceso(request, subproceso_id):
    subproceso = get_object_or_404(Subproceso, pk=subproceso_id)
    tareas = subproceso.tareas.all()  # Esto recupera todas las tareas relacionadas

    return render(request, 'subprocesos/ver_subproceso.html', {
        'subproceso': subproceso,
        'tareas': tareas
    })

def editar_subproceso(request, subproceso_id):
    subproceso = get_object_or_404(Subproceso, pk=subproceso_id)
    logging.error("eli")
    if request.method == 'POST':
        logging.error("eli")
        form = SubprocesoEditForm(request.POST, instance=subproceso)
        if form.is_valid():
            logging.error("valid")
            subproceso = form.save()
            return redirect('lista_subprocesos')
    else:
        form = SubprocesoEditForm(instance=subproceso)
    return render(request, 'subprocesos/editar_subproceso.html', {'form': form})

#
#   TAREAS
#
def lista_tareas(request):
    tareas = Tarea.objects.all()
    return render(request, 'tareas/lista_tareas.html', {'tareas': tareas})


# creacion de procesos con subprocesos
#creacion de procesos
def mi_vista_compleja(request, proceso_id=None, subproceso_id=None):
    # Inicializa el formulario de Proceso con un posible proceso existente
    proceso = Proceso.objects.filter(pk=proceso_id).first() if proceso_id else None
    proceso_form = ProcesoForm(request.POST or None, prefix="proceso", instance=proceso)
    subproceso_form = SubprocesoForm(request.POST or None, prefix="subproceso")
    tarea_form = TareaPruebaForm(request.POST or None, prefix="tarea")


    if 'submit_proceso' in request.POST and proceso_form.is_valid():
        proceso = proceso_form.save()
        proceso_id = proceso.id  # Actualiza el proceso_id con el id del proceso guardado

        if subproceso_id is not None:
            return redirect('procesos_con_id', proceso_id=proceso_id, subproceso_id=subproceso_id)
        else:
            return redirect('procesos_con_id', proceso_id=proceso_id)

    elif 'submit_subproceso' in request.POST and subproceso_form.is_valid():
        subproceso = subproceso_form.save(commit=False)
        subproceso.save()
        subproceso_id = subproceso.id
        # Aquí asociamos el proceso actual al subproceso
        if proceso_id:
            proceso = Proceso.objects.get(pk=proceso_id)
            subproceso.proceso.add(proceso)
        return redirect('procesos_con_id', proceso_id=proceso_id, subproceso_id=subproceso_id)

    elif 'submit_tarea' in request.POST and tarea_form.is_valid():
        tarea = tarea_form.save(commit=False)
        tarea.save()
        # Suponiendo que has capturado un subproceso_id de alguna manera
        if subproceso_id:
            subproceso = Subproceso.objects.get(pk=subproceso_id)
            tarea.subproceso.add(subproceso)
        return redirect('procesos_con_id', proceso_id=proceso_id, subproceso_id=subproceso_id)

    procesos = Proceso.objects.filter(pk=proceso_id).prefetch_related('subprocesos__tareas') if proceso_id else Proceso.objects.none()


    return render(request, 'procesos/procesos.html', {
        'proceso_form': proceso_form,
        'subproceso_form': subproceso_form,
        'tarea_form': tarea_form,
        'procesos': procesos,
    })
