from django.views.generic import TemplateView

from .forms import NewGroupTarjetaForm
from .utils import MONTHS, obtener_tarjetas_del_dia, verificar_tarjetas_del_mes, informe_tarjetas_del_mes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from pruebas.models import NewTarjeta, NewOrden, NewTarea
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from pruebas.models import NewTarjeta
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from django.contrib import messages
import calendar

class CalendarioMesView(LoginRequiredMixin, TemplateView):
    template_name = 'calendario_mes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user  # Obtiene el usuario logueado
        try:
            datos_mes = verificar_tarjetas_del_mes(usuario)
            context['mes'] = datos_mes.get('mes', 'No disponible')
            context['anio'] = datos_mes.get('anio', 'No disponible')
            context['dias'] = datos_mes.get('dias', [])
        except Exception as e:
            context['error'] = f"Error al obtener los datos: {str(e)}"
        return context
    
class InformeTarjetasMesView(TemplateView):
    template_name = 'informe_tarjetas_mes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener los parámetros del URL
        mes = self.kwargs.get('mes')
        anio = self.kwargs.get('anio')
        
        # Obtener los datos del informe para el mes y año especificados
        datos_informe = informe_tarjetas_del_mes(mes, anio)
        
        context['mes'] = datos_informe['mes']
        context['anio'] = datos_informe['anio']
        context['informe'] = datos_informe['informe_por_usuario']
        return context

def tarjeta_usuario_dia(request, usuario_id, dia):
    usuario = get_object_or_404(User, pk=usuario_id)
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    
    if not mes or not anio:
        messages.error(request, 'Mes o año no válidos')
        return redirect('informe-tarjetas-mes') 
    
    try:
        mes_numero = list(calendar.month_name).index(mes)
        fecha = datetime.strptime(f"{dia}-{mes_numero}-{anio}", "%d-%m-%Y").date()
    except ValueError as e:
        messages.error(request, f"Error al parsear la fecha: {e}")
        return redirect('informe-tarjetas-mes') 
    
    tarjeta = get_object_or_404(NewTarjeta, usuario=usuario, fecha=fecha)

    base_time = datetime.strptime('08:00', '%H:%M').time()
    current_time = base_time
    tareas_con_hora = []
    for tarea in tarjeta.get_ordered_tareas():
        end_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=float(tarea.tiempo_tarea))).time()
        relacion = tarea.neworden_set.filter(tarjeta=tarjeta).first()
        tareas_con_hora.append({
            'tarea': tarea,
            'start_time': current_time,
            'end_time': end_time,
            'relacion_id': relacion.id if relacion else None,
            'estado': relacion.estado if relacion else ''
        })
        current_time = end_time
    tarjeta.tareas_con_hora = tareas_con_hora
    tarjeta.incidents_list = tarjeta.incidents.all()

    context = {
        'tarjeta': tarjeta,
        'tareas_con_hora': tareas_con_hora,
        'porcentaje_completado': tarjeta.porcentaje_completado,
        'porcentaje_incidentes': tarjeta.porcentaje_incidentes,
        'valorizacion': tarjeta.valorizacion
    }
    return render(request, 'tarjeta_usuario_dia.html', context)

def eliminar_tarjeta(request, usuario_id, dia):
    usuario = get_object_or_404(User, pk=usuario_id)
    mes = request.POST.get('mes')
    anio = request.POST.get('anio')

    if not mes or not anio:
        messages.error(request, 'Mes o año no válidos')
        return redirect('informe_tarjetas_mes')  # Redirige a la vista de informes mensuales si los valores no son válidos

    try:
        mes_numero = int(mes)
        anio = int(anio)
        fecha = datetime.strptime(f"{dia}-{mes}-{anio}", "%d-%m-%Y").date()
    except ValueError as e:
        messages.error(request, f"Error al parsear la fecha: {e}")
        return redirect('informe_tarjetas_mes', mes=mes, anio=anio)  # Redirige a la vista de informes mensuales si hay un error de parseo

    tarjeta = get_object_or_404(NewTarjeta, usuario=usuario, fecha=fecha)
    tarjeta.delete()
    messages.success(request, 'Tarjeta eliminada exitosamente')
    return redirect('informe_tarjetas_mes', mes=mes_numero, anio=anio)

@login_required
def crear_tarjeta_para_usuario(request, usuario_id, dia, mes, anio):
    usuario = get_object_or_404(User, pk=usuario_id)
    mes_num = MONTHS.get(mes)
    
    if not mes_num or not anio:
        return render(request, 'error.html', {'message': 'Mes o año no válidos'})

    fecha = datetime.strptime(f"{dia}-{mes_num}-{anio}", "%d-%m-%Y").date()
    
    # Filtrar las tareas incompletas y reprogramadas del usuario
    tareas_incompletas = NewTarea.objects.filter(
        neworden__estado='incompleta',
        neworden__tarjeta__usuario=usuario
    ).distinct()
    
    tareas_reprogramadas = NewTarea.objects.filter(
        neworden__estado='reprogramada',
        neworden__tarjeta__usuario=usuario
    ).distinct()
    
    if request.method == "POST":
        form = NewGroupTarjetaForm(request.POST, user=usuario)
        if form.is_valid():
            with transaction.atomic():
                tarjeta = form.save(commit=False)
                tarjeta.usuario = usuario
                tarjeta.fecha = fecha
                tarjeta.save()
                
                tareas = form.cleaned_data['tareas']
                ordenes = [NewOrden(tarjeta=tarjeta, tarea=tarea, order=order) for order, tarea in enumerate(tareas, start=1)]
                NewOrden.objects.bulk_create(ordenes)

                return redirect('informe_tarjetas_mes', anio=anio, mes=mes_num)
    else:
        form = NewGroupTarjetaForm(user=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'fecha': fecha,
        'tareas_incompletas': tareas_incompletas,
        'tareas_reprogramadas': tareas_reprogramadas
    }
    return render(request, 'nueva_tarjeta_para_usuario.html', context)

def ver_tarjeta_equipo(request):
    hoy = date.today()
    tarjetas = obtener_tarjetas_del_dia(hoy)

    # Agrupar las tarjetas por usuario
    informe = {}
    for tarjeta in tarjetas:
        usuario_id = tarjeta.usuario.id
        if usuario_id not in informe:
            informe[usuario_id] = {
                'usuario': tarjeta.usuario.username,
                'dias_con_tarjeta': []
            }
        informe[usuario_id]['dias_con_tarjeta'].append(tarjeta.fecha.day)

    context = {
        'informe': informe,
    }
    
    return render(request, 'ver_tarjeta_equipo.html', context)