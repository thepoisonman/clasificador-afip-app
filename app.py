
import streamlit as st
import pandas as pd
import requests
import os

st.title("Clasificador de Comprobantes AFIP")

# Subir archivo Excel
uploaded_file = st.file_uploader("Subí tu archivo de comprobantes AFIP (Compras o Mis Comprobantes Recibidos)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df = pd.read_excel(uploaded_file, sheet_name=xls.sheet_names[0], skiprows=1)

    # Normalizar columnas según el formato
    if 'Nro. Doc. Emisor' in df.columns:
        # Formato "Mis Comprobantes Recibidos"
        df.rename(columns={
            'Nro. Doc. Emisor': 'CUIT',
            'Denominación Emisor': 'Proveedor',
            'Imp. Total': 'Total'
        }, inplace=True)
    elif 'CUIT' in df.columns:
        # Formato "Comprobantes de Compras"
        pass  # ya está bien
    else:
        st.error("⚠️ Formato de archivo no reconocido. Subí un archivo exportado de AFIP.")
        st.stop()

    st.write("📄 Comprobantes cargados:")
    st.dataframe(df)

    api_key = os.getenv("CUIT_API_KEY", "api_key_demo")

    def buscar_categoria(cuit):
        url = f"https://cuitonline.com/api/v1/companies/{cuit}?api-key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            actividad = data.get("actividad_principal", "Sin info")
            return actividad
        return "No encontrado"

    st.write("🔍 Consultando CUIT Online...")
    df["Actividad"] = df["CUIT"].astype(str).apply(buscar_categoria)

    st.write("📊 Resultado con Actividad:")
    st.dataframe(df)
    