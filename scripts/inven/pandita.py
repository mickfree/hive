import pandas as pd

# Carga el archivo Excel
file_path = 'Inventario.xlsx'  # Cambia esto por la ruta de tu archivo
data = pd.read_excel(file_path)

# Asegurarte de que todos los valores en 'Grupo' son strings y no nulos
data['Grupo'] = data['Grupo'].fillna('UNNAMED')
data['Grupo'] = data['Grupo'].apply(lambda x: 'UNNAMED' if pd.isna(x) or x.strip() == '' else x.strip())

# Lista de grupos conocidos
grupos_conocidos = ['EQUIPOS', 'CONSUMIBLES', 'MATERIALES', 'VENTA DE SERVICIOS', 'HERRAMIENTAS',
                    'MANTENIMIENTO', 'EPPS', 'MANO DE OBRA', 'ALQUILERES', 'ANDAMIO', 'FABRICACION', 'TRANSPORTE']

# Reasignar valores que no están en la lista de grupos conocidos a 'UNNAMED'
data['Grupo'] = data['Grupo'].apply(lambda x: x if x in grupos_conocidos else 'UNNAMED')

# Crear un nuevo archivo Excel para guardar los resultados
writer = pd.ExcelWriter('data_main.xlsx', engine='openpyxl')

# Agrupar los datos por la columna 'Grupo' y escribir cada grupo en una hoja diferente
for group_name, group_data in data.groupby('Grupo'):
    # Limpiar el nombre del grupo para que sea válido como nombre de hoja
    clean_group_name = group_name.replace('/', '-').replace('\\', '-').replace(':', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
    clean_group_name = clean_group_name[:31]  # Excel limita los nombres de las hojas a 31 caracteres
    
    # Escribir los datos del grupo en una hoja del archivo Excel
    group_data.to_excel(writer, sheet_name=clean_group_name, index=False)

# Cerrar y guardar el archivo Excel
writer.close()
