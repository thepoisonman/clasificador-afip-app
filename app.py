
import streamlit as st
import pandas as pd
import requests

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu archivo de comprobantes AFIP (Excel)", type=["xlsx"])

API_KEY = "prueba_demo_api_key"
API_URL = "https://api.cuitonline.com/v1/constancia"

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if 'CUIT' not in df.columns:
        st.error("El archivo no tiene columna 'CUIT'. Verificá el formato.")
    else:
        gastos = []
        for cuit in df['CUIT']:
            response = requests.get(f"{API_URL}/{cuit}?apikey={API_KEY}")
            if response.status_code == 200:
                data = response.json()
                actividad = data.get("actividadPrincipal", "Desconocido")
                gastos.append(actividad)
            else:
                gastos.append("No encontrado")
        
        df['Concepto Detectado'] = gastos

        conceptos_unicos = df['Concepto Detectado'].unique()
        for concepto in conceptos_unicos:
            nuevo = st.text_input(f"Asignar tipo de gasto a: {concepto}", value=concepto)
            df.loc[df['Concepto Detectado'] == concepto, 'Tipo de Gasto'] = nuevo

        output_path = "/mnt/data/comprobantes_clasificados.xlsx"
        df.to_excel(output_path, index=False)
        st.success("Clasificación finalizada.")
        st.download_button("Descargar archivo clasificado", output_path)
