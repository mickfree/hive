from datetime import date, timedelta
from django.utils import timezone
from pruebas.models import NewTarjeta 
from datetime import date, timedelta
from django.utils import timezone
from pruebas.models import NewTarjeta
from django.contrib.auth.models import User


def verificar_tarjetas_del_mes(usuario):
    hoy = timezone.now().date()  
    primer_dia_mes = date(hoy.year, hoy.month, 1)
    ultimo_dia_mes = primer_dia_mes + timedelta(days=28) + timedelta(days=4)
    ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

    # Filtrar las tarjetas según el usuario
    dias_con_tarjeta = set(NewTarjeta.objects.filter(
        usuario=usuario,  # Filtrar por usuario
        fecha__range=(primer_dia_mes, ultimo_dia_mes)
    ).values_list('fecha', flat=True))

    dias_del_mes = []
    for i in range((ultimo_dia_mes - primer_dia_mes).days + 1):
        dia_actual = primer_dia_mes + timedelta(days=i)
        tiene_tarjeta = dia_actual in dias_con_tarjeta
        dias_del_mes.append({
            'fecha': dia_actual,
            'tiene_tarjeta': tiene_tarjeta
        })

    return {
        'mes': primer_dia_mes.strftime('%B'),
        'anio': primer_dia_mes.year,
        'dias': dias_del_mes
    }

def informe_tarjetas_del_mes(mes, anio):
    primer_dia_mes = date(anio, mes, 1)
    ultimo_dia_mes = primer_dia_mes + timedelta(days=28) + timedelta(days=4)
    ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

    # Traer las tarjetas de todos los usuarios para el mes
    tarjetas_del_mes = NewTarjeta.objects.filter(
        fecha__range=(primer_dia_mes, ultimo_dia_mes)
    ).order_by('usuario', 'fecha')

    # Preparar la estructura de datos para almacenar los resultados
    informe = {}
    for tarjeta in tarjetas_del_mes:
        usuario_id = tarjeta.usuario.id
        if usuario_id not in informe:
            informe[usuario_id] = {
                'usuario': tarjeta.usuario.username,
                'dias_con_tarjeta': set(),
                'dias_sin_tarjeta': set(range(1, (ultimo_dia_mes - primer_dia_mes).days + 2))
            }
        informe[usuario_id]['dias_con_tarjeta'].add(tarjeta.fecha.day)
        informe[usuario_id]['dias_sin_tarjeta'].discard(tarjeta.fecha.day)

    # Convertir los sets a listas para que sean JSON serializables si es necesario
    for usuario_id, datos in informe.items():
        datos['dias_con_tarjeta'] = sorted(list(datos['dias_con_tarjeta']))
        datos['dias_sin_tarjeta'] = sorted(list(datos['dias_sin_tarjeta']))

    return {
        'mes': primer_dia_mes.strftime('%B'),
        'anio': primer_dia_mes.year,
        'informe_por_usuario': informe
    }

MONTHS = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}

def obtener_tarjetas_del_dia(fecha=None):
    hoy = timezone.now().date()
    if fecha:
        primer_dia_mes = fecha
    else:
        primer_dia_mes = date(hoy.year, hoy.month, 1)
    
    tarjetas_del_dia = NewTarjeta.objects.filter(
        fecha=primer_dia_mes
    ).order_by('usuario', 'fecha')
    
    return tarjetas_del_dia


