
import os
import pandas as pd

# Ruta de salida
output_dir = 'outputs'
output_path = os.path.join(output_dir, 'resultado.xlsx')

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

# DataFrame de prueba
data = {'CUIT': ['20123456789'], 'Concepto': ['Servicios']}
df = pd.DataFrame(data)

# Guardar en Excel
df.to_excel(output_path, index=False)

print("Archivo guardado en", output_path)
