
import streamlit as st
import pandas as pd
import os
import requests

# Configuración
API_URL = "https://cuitonline.com/api/v1/cuit/"
API_KEY = "prueba"

# Crear carpeta outputs si no existe
os.makedirs("outputs", exist_ok=True)

st.title("Clasificador AFIP App")

uploaded_file = st.file_uploader("Subí tu archivo de compras AFIP (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=1)

    # Verificar si existe la columna CUIT
    if "CUIT" not in df.columns:
        st.error("El archivo no tiene columna 'CUIT'. Verificá el formato.")
    else:
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())

        proveedor_col = st.selectbox("Seleccioná la columna de proveedores:", df.columns, index=8)

        # Consultar CUIT Online API
        actividades = []
        for cuit in df["CUIT"].astype(str):
            response = requests.get(f"{API_URL}{cuit}?key={API_KEY}")
            if response.status_code == 200:
                data = response.json()
                actividad = data.get("actividad", "No encontrada")
            else:
                actividad = "No encontrada"
            actividades.append(actividad)

        df["Actividad"] = actividades

        # Refinación manual de conceptos
        conceptos = []
        for proveedor in df[proveedor_col]:
            concepto = st.text_input(f"Concepto para {proveedor}:", "")
            conceptos.append(concepto)

        df["Concepto"] = conceptos

        output_path = "outputs/comprobantes_clasificados.xlsx"
        df.to_excel(output_path, index=False)
        st.success(f"Archivo guardado en {output_path}")
        with open(output_path, "rb") as f:
            st.download_button("Descargar Excel Clasificado", f, file_name="comprobantes_clasificados.xlsx")
