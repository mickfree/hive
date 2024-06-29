# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import NewTarea, Incident, NewOrden
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import NewTarea, Incident, NewOrden, NewTarjeta
from django.db import models

@receiver(post_save, sender=NewTarea)
@receiver(post_delete, sender=NewTarea)
@receiver(post_save, sender=Incident)
@receiver(post_delete, sender=Incident)
@receiver(post_save, sender=NewOrden)
@receiver(post_delete, sender=NewOrden)
def handle_update_tarjeta_fields(sender, instance, **kwargs):
    tarjetas = []

    if isinstance(instance, NewOrden):
        tarjeta = instance.tarjeta
        tarjetas.append(tarjeta)
    elif isinstance(instance, NewTarea):
        tarjetas = list(instance.tarjetas.all())
    elif isinstance(instance, Incident):
        tarjetas = [instance.tarjeta]

    for tarjeta in tarjetas:
        update_tarjeta_fields(tarjeta)

def update_tarjeta_fields(tarjeta):
    ordered_tareas = tarjeta.get_ordered_tareas()
    incidents = tarjeta.incidents.all()

    # Calcula los minutos totales de las tareas
    total_minutos = sum(tarea.tiempo_tarea for tarea in ordered_tareas if tarea.tiempo_tarea)
    # Calcula los minutos de las tareas completadas
    total_minutos_completados = sum(
        tarea.tiempo_tarea for tarea in ordered_tareas
        if tarea.tiempo_tarea and tarea.neworden_set.filter(tarjeta=tarjeta, estado='completa').exists()
    )
    # Calcula los minutos totales de incidentes
    total_minutos_incidentes = sum(incidente.duracion for incidente in incidents)

    # Calcula los porcentajes
    if total_minutos > 0:
        porcentaje_completado = round((total_minutos_completados / total_minutos) * 100, 2)
        porcentaje_incidentes = round((total_minutos_incidentes / total_minutos) * 100, 2)
    else:
        porcentaje_completado = 0
        porcentaje_incidentes = 0

    # Asigna los valores calculados a la tarjeta
    tarjeta.total_minutos = total_minutos
    tarjeta.total_minutos_completados = total_minutos_completados
    tarjeta.total_minutos_incidentes = total_minutos_incidentes
    tarjeta.porcentaje_completado = porcentaje_completado
    tarjeta.porcentaje_incidentes = porcentaje_incidentes
    tarjeta.valorizacion = calculate_valorizacion(porcentaje_completado)
    
    # Guarda los cambios en la tarjeta
    tarjeta.save()

def calculate_valorizacion(porcentaje_completado):
    if porcentaje_completado >= 90:
        return 'A'
    elif porcentaje_completado >= 75:
        return 'B'
    elif porcentaje_completado >= 50:
        return 'C'
    else:
        return 'D'
