import csv

# Nombre del archivo original y el archivo nuevo
archivo_original = 'inventario_inventario.csv'
archivo_separado = 'archivo_separado.csv'

# Función para limpiar las celdas
def limpiar_celda(celda):
    return celda.strip().replace('"""', '').replace('""', '').replace('""""', '')

# Leemos el archivo original y escribimos en el nuevo archivo
with open(archivo_original, 'r', encoding='utf-8') as csvfile:
    lector_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
    with open(archivo_separado, 'w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        
        for linea in lector_csv:
            linea_limpia = [limpiar_celda(celda) for celda in linea]
            escritor_csv.writerow(linea_limpia)

print("Archivo separado y limpiado guardado en", archivo_separado)
