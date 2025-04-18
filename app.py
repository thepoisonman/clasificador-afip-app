
import streamlit as st
import pandas as pd
import json
import os
from utils.clasificador import clasificar_gastos
from utils.refinador import refinar_conceptos

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

    # Detectar columnas CUIT y Proveedor
    cuit_col = next((col for col in df.columns if df[col].astype(str).str.contains(r'\d{7,8,11}').any()), None)
    proveedor_col = next((col for col in df.columns if 'mercado' in df[col].astype(str).str.lower().values or 'proveedor' in col.lower()), None)

    if cuit_col and proveedor_col:
        df['CUIT'] = df[cuit_col]
        df['Proveedor'] = df[proveedor_col]
        df['Concepto Detectado'] = df.apply(lambda row: clasificar_gastos(row['Proveedor'], row['CUIT'], memoria), axis=1)

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
            memoria[f"{df.iloc[i]['CUIT']}|{df.iloc[i]['Proveedor']}"] = concepto_manual

        refined_output = f"outputs/comprobantes_refinados.xlsx"
        df.to_excel(refined_output, index=False)
        st.success(f"Archivo refinado generado: {refined_output}")

        with open("memory.json", "w") as f:
            json.dump(memoria, f, indent=4)

    else:
        st.error("No se detectaron correctamente las columnas de CUIT y Proveedor.")
