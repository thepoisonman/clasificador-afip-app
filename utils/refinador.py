
import json
import os

def refinar_conceptos(df, memory_path):
    if os.path.exists(memory_path):
        with open(memory_path, 'r') as f:
            memoria = json.load(f)
    else:
        memoria = {}

    for i, row in df.iterrows():
        cuit = str(row['CUIT'])
        concepto_detectado = row['Concepto Detectado']
        concepto_memorizado = memoria.get(cuit)
        if concepto_memorizado:
            df.at[i, 'Concepto Detectado'] = concepto_memorizado

    return df

def guardar_refinamientos(cambios, memory_path):
    if os.path.exists(memory_path):
        with open(memory_path, 'r') as f:
            memoria = json.load(f)
    else:
        memoria = {}

    memoria.update(cambios)

    with open(memory_path, 'w') as f:
        json.dump(memoria, f, indent=4)
