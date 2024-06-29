import csv
import re

# Ruta del archivo CSV
input_file = 'inventario_inventario.csv'

# Diccionarios para guardar datos de cada grupo de artículos
output_files = {
    'EQUIPOS': 'equipos.txt',
    'EPPS': 'epps.txt',
    'TRANSPORTE': 'transporte.txt',
    'MATERIALES': 'materiales.txt',
    'CONSUMIBLES': 'consumibles.txt',
    'ALIMENTOS': 'alimentos.txt',
    'MANODEOBRA': 'manodeobra.txt',
    'HERRAMIENTAS': 'herramientas.txt',
    'MISC': 'misc.txt',
}

# Inicializa los archivos de salida
file_handlers = {key: open(value, 'w', encoding='utf-8') for key, value in output_files.items()}

# Abre el archivo CSV original
with open(input_file, 'r', encoding='utf-8') as csvfile:
    content = csvfile.read()
    
    # Reemplaza caracteres extraños y limpia el contenido
    content = re.sub(r'\n+', '\n', content)
    content = re.sub(r';;', '', content)
        
    # Divide el contenido por líneas
    lines = content.split('\n')
    
    # Limpia y prepara los encabezados
    headers = [
        "id", "num_articulo", "descripcion", "en_stock", "codigo_barras",
        "grupo_articulos", "fabricante", "unidad_medida", "ultima_revalorizacion",
        "ultimo_precio_compra"
    ]

    # Escribe los encabezados en cada archivo de salida
    for handler in file_handlers.values():
        handler.write(','.join(headers) + '\n')

    # Inicializa un acumulador de líneas
    current_row = []
    in_quotes = False

    for line in lines[1:]:
        if not line.strip():
            continue  # Salta las líneas vacías
        
        if line.count('"') % 2 != 0:
            in_quotes = not in_quotes
            current_row.append(line)
        else:
            current_row.append(line)
            if not in_quotes:
                row = ' '.join(current_row)
                current_row = []
                # Limpia y separa las columnas
                row = re.sub(r'""', '"', row)
                row = re.sub(r'","', '\",\"', row)
                row = re.sub(r'^"|"$', '', row)
                row = row.split('","')
                if len(row) < 6:
                    continue  # Salta las filas que no tienen suficientes columnas
                grupo_articulos = row[5].strip()
                if grupo_articulos in file_handlers:
                    file_handlers[grupo_articulos].write(','.join(row) + '\n')

# Cierra todos los archivos
for handler in file_handlers.values():
    handler.close()
