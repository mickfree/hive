from ordenventa.models import OrdenDeCompra
from django.shortcuts import render
from extractos.models import Banco, ExtractosBancarios

def conciliacion(request):
    banco_id = request.GET.get('banco', None)
    ordenes_query = OrdenDeCompra.objects.all()
    extractos_query = ExtractosBancarios.objects.all()

    if banco_id:
        ordenes_query = ordenes_query.filter(banco_relacionado_id=banco_id)
        extractos_query = extractos_query.filter(banco_id=banco_id)

    ordenes = ordenes_query.values(
        'proveedor__nombre_proveedor',
        'monto_pagado',
        'numero_movimiento_bancario',
        'banco_relacionado__nombre_banco'
    )
    extractos = extractos_query.values(
        'numero_movimiento',
        'importe',
        'banco__nombre_banco'
    )

    coincidencias = [
        {
            'orden': orden,
            'extracto': extracto
        }
        for orden in ordenes
        for extracto in extractos
        if orden['numero_movimiento_bancario'] == extracto['numero_movimiento']
    ]

    # Pasar la lista de bancos al template para construir el selector de bancos
    bancos = Banco.objects.all()

    # Retornar los datos a una plantilla simple para visualizar
    return render(request, 'conciliacion.html', {
        'coincidencias': coincidencias,
        'bancos': bancos
    })
