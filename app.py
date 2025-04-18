
import streamlit as st
import pandas as pd
import os
import json
import re

# Crear carpetas necesarias
os.makedirs('outputs', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Cargar memoria
if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        memoria = json.load(f)
else:
    memoria = {}

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu Excel de comprobantes AFIP", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Excluir la primera fila si es un encabezado de datos
    if df.iloc[0].str.contains("Fecha").any():
        df = df[1:].reset_index(drop=True)

    # Deducción de CUIT/DNI y Proveedor a partir de los datos de la columna
    def es_cuit_o_dni(value):
        # Validar si es un CUIT (11 dígitos) o un DNI (7-8 dígitos)
        value = str(value).strip()
        return len(value) >= 7 and len(value) <= 11 and value.isdigit()

    cuit_col = None
    proveedor_col = None

    # Detectar CUIT/DNI y Proveedor
    for col in df.columns:
        if df[col].apply(es_cuit_o_dni).sum() > 0:
            cuit_col = col
        elif df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, str) and not es_cuit_o_dni(x)).sum() > 0:
            proveedor_col = col

    # Deducción adicional para proveedor basado en denominaciones societarias
    if proveedor_col is None:
        denominaciones = ["SA", "SRL", "SAS", "S.C.A.", "S.A.", "S.R.L.", "S.A.S."]
        for col in df.columns:
            for denominacion in denominaciones:
                if df[col].apply(lambda x: isinstance(x, str) and denominacion in x).sum() > 0:
                    proveedor_col = col
                    break
            if proveedor_col:
                break

    if cuit_col and proveedor_col:
        df['CUIT'] = df[cuit_col]
        df['Proveedor'] = df[proveedor_col]
        df['Concepto Detectado'] = df.apply(lambda row: memoria.get(row['CUIT'], "Otros"), axis=1)

        st.dataframe(df)

        output_file = f"outputs/comprobantes_clasificados.xlsx"
        df.to_excel(output_file, index=False)
        st.success(f"Archivo clasificado generado: {output_file}")

        st.subheader("Refinar conceptos manualmente")
        for i in range(len(df)):
            concepto_manual = st.text_input(f"Concepto para {df.iloc[i]['Proveedor']} ({df.iloc[i]['CUIT']})",
                                            df.iloc[i]["Concepto Detectado"],
                                            key=f"concepto_{i}")
            df.at[i, "Concepto Detectado"] = concepto_manual
            memoria[df.iloc[i]['CUIT']] = concepto_manual

        refined_output = f"outputs/comprobantes_refinados.xlsx"
        df.to_excel(refined_output, index=False)
        st.success(f"Archivo refinado generado: {refined_output}")

        with open("memory.json", "w") as f:
            json.dump(memoria, f, indent=4)

    else:
        st.error("No se detectaron correctamente las columnas de CUIT y Proveedor.")
