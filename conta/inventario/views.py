import openpyxl
from django.shortcuts import redirect, render

from inventario.forms import InventarioForm, UploadExcelForm
from .models import Inventario
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
import re

def inventario(request):
    inventario = Inventario.objects.all()

    if request.method == 'POST' and 'eliminar_todo' in request.POST:
        # Eliminar todos los archivos del inventario
        Inventario.objects.all().delete()
        return redirect('inventario')  # Redirigir a la misma página después de la eliminación

    return render(request, 'inventario.html', {'inventario': inventario})
class AgregarItemInventario(FormView):
    template_name = 'agregar_item_inventario.html'
    form_class = InventarioForm
    success_url = reverse_lazy('inventario')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

def procesar_excel(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            wb = openpyxl.load_workbook(filename=archivo_excel, read_only=True)
            sheet = wb['INVENTARIO']

            for row in sheet.iter_rows(min_row=2, values_only=True):
                num_articulo, descripcion, en_stock, codigo_barras, grupo_articulos, fabricante, unidad_medida, ultima_revalorizacion, ultimo_precio_compra = row[:9]

                # Verificar y proporcionar valores predeterminados para campos nulos o vacíos
                num_articulo = num_articulo or 'No disponible'
                descripcion = descripcion or 'Sin descripción'
                en_stock = en_stock if en_stock is not None else 0
                codigo_barras = codigo_barras or 'No disponible'
                grupo_articulos = grupo_articulos or 'No disponible'
                fabricante = fabricante or 'No disponible'
                unidad_medida = unidad_medida or 'No disponible'
                ultima_revalorizacion = ultima_revalorizacion if ultima_revalorizacion is not None else 0
                ultimo_precio_compra = ultimo_precio_compra if ultimo_precio_compra is not None else 0

                    # Limpiar y formatear el valor de ultima_revalorizacion
                ultima_revalorizacion = str(ultima_revalorizacion)  # Convertir a cadena de texto
                ultima_revalorizacion = re.sub('[^\d.]', '', ultima_revalorizacion)  # Eliminar caracteres no numéricos excepto el punto decimal
                ultima_revalorizacion = float(ultima_revalorizacion) if ultima_revalorizacion else 0.0  # Convertir a float, establecer en 0 si es vacío

                # Limpiar y formatear el valor de ultimo_precio_compra
                ultimo_precio_compra = str(ultimo_precio_compra)  # Convertir a cadena de texto
                ultimo_precio_compra = re.sub('[^\d.]', '', ultimo_precio_compra)  # Eliminar caracteres no numéricos excepto el punto decimal
                ultimo_precio_compra = float(ultimo_precio_compra) if ultimo_precio_compra else 0.0  # Convertir a float, establecer en 0 si es vacío



                Inventario.objects.create(
                    num_articulo=num_articulo,
                    descripcion=descripcion,
                    en_stock=en_stock,
                    codigo_barras=codigo_barras,
                    grupo_articulos=grupo_articulos,
                    fabricante=fabricante,
                    unidad_medida=unidad_medida,
                    ultima_revalorizacion=ultima_revalorizacion,
                    ultimo_precio_compra=ultimo_precio_compra
                )

            return redirect('inventario')
    else:
        form = UploadExcelForm()

    return render(request, 'upload_excel.html', {'form': form})
