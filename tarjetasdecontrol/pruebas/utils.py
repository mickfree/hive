import requests
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction
from .models import NewTarea

def obtener_datos_api():
    import requests

    url = 'https://proyectos.awlmaquitec.com/projects/apiprojects/'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error al obtener datos de la API:", e)
        return {}

    try:
        data = response.json()
    except ValueError as e:
        print("Error al convertir respuesta a JSON:", e)
        return {}

    # Convertir a una lista de tuplas [(ov_name, client_name)]
    ordenes_list = [(item['ov_name'], item['client']['client_name']) for item in data]

    print("Datos obtenidos de la API:", ordenes_list)

    return ordenes_list

def recalculate_task_start_times(tarjeta):
    base_time = datetime.strptime('08:00', '%H:%M').time()
    current_time = base_time
    ordered_tareas = tarjeta.get_ordered_tareas()

    recalculated_times = []

    for tarea in ordered_tareas:
        start_time = current_time
        end_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=float(tarea.tiempo_tarea))).time()
        recalculated_times.append({
            'tarea': tarea,
            'calculated_start_time': start_time,
            'end_time': end_time
        })
        current_time = end_time

    return recalculated_times
