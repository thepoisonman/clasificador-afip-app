
import streamlit as st
import pandas as pd
import requests
import os

st.title("Clasificador AFIP - Prueba CUIT Online")

uploaded_file = st.file_uploader("Subí tu archivo de compras AFIP (Excel)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Intentar ubicar la columna CUIT correctamente (en la posición 7 según indicaste)
    cuit_col = df.columns[6]  # posición 7 -> índice 6
    proveedor_col = df.columns[7]  # posición 8 -> índice 7

    st.write("CUIT detectado en columna:", cuit_col)
    st.write("Proveedor detectado en columna:", proveedor_col)

    # Limpiar encabezados erróneos
    df = df[df[cuit_col].astype(str).str.contains(r'^[0-9]{11}$', na=False)]

    def obtener_concepto(cuit):
        api_key = "DEMO-API-KEY"
        url = f"https://api.cuitonline.com/afip/v1/persona/{cuit}?apikey={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("actividad", "No encontrada")
            else:
                return "Error API"
        except:
            return "Error de conexión"

    df["Concepto Detectado"] = df[cuit_col].apply(obtener_concepto)

    st.write("Vista previa del archivo:")
    st.dataframe(df[[proveedor_col, cuit_col, "Concepto Detectado"]])

    # Corrección de conceptos manual
    conceptos_refinados = []
    for i in range(len(df)):
        concepto_manual = st.text_input(
            f"Concepto para {df.iloc[i][proveedor_col]} ({df.iloc[i][cuit_col]})",
            df.iloc[i]["Concepto Detectado"],
            key=f"concepto_{i}"
        )
        conceptos_refinados.append(concepto_manual)

    df["Concepto Final"] = conceptos_refinados

    # Descargar archivo corregido
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    output_path = "outputs/comprobantes_clasificados.xlsx"
    df.to_excel(output_path, index=False)

    with open(output_path, "rb") as file:
        btn = st.download_button(
            label="📥 Descargar Excel Clasificado",
            data=file,
            file_name="comprobantes_clasificados.xlsx"
        )
    