
import streamlit as st
import pandas as pd
import requests
import os

# Crear carpeta outputs si no existe
if not os.path.exists("outputs"):
    os.makedirs("outputs")

st.title("Clasificador AFIP App")

uploaded_file = st.file_uploader("Subí tu archivo de comprobantes AFIP", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Eliminar encabezados fantasma (filas donde 'Fecha' o 'Tipo' aparecen en la primera columna)
    df = df[~df.iloc[:, 0].astype(str).str.contains("Fecha|Tipo", case=False, na=False)].copy()

    # Renombrar columnas por posición fija (según formato AFIP)
    df.columns = ['Fecha', 'Tipo', 'Punto de Venta', 'Número Desde', 'Número Hasta', 'Tipo Doc. Vendedor',
                  'CUIT', 'Proveedor', 'Importe'] + list(df.columns[9:])

    # Consulta automática a CUIT Online
    api_key = "PRUEBA_API_KEY"
    conceptos = []
    for cuit in df['CUIT']:
        try:
            response = requests.get(f"https://api.cuitonline.com/cuit/{cuit}/{api_key}")
            if response.status_code == 200:
                data = response.json()
                actividad = data.get("actividad", "No encontrado")
                conceptos.append(actividad)
            else:
                conceptos.append("No encontrado")
        except:
            conceptos.append("Error")

    df["Concepto Detectado"] = conceptos

    # Permitir corrección manual
    for i in range(len(df)):
        concepto_manual = st.text_input(f"Concepto para {df.iloc[i]['Proveedor']}", df.iloc[i]["Concepto Detectado"])
        df.at[i, "Concepto Detectado"] = concepto_manual

    # Guardar Excel
    output_path = "outputs/clasificados.xlsx"
    df.to_excel(output_path, index=False)

    st.success(f"Archivo procesado y guardado en {output_path}")
    with open(output_path, "rb") as file:
        st.download_button("Descargar resultado", file, file_name="clasificados.xlsx")
