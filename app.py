
import streamlit as st
import pandas as pd
import requests
import os

st.title("Clasificador AFIP App")

uploaded_file = st.file_uploader("Subí tu archivo de comprobantes AFIP", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if 'CUIT' not in df.columns:
        st.error("El archivo no tiene columna 'CUIT'. Verificá el formato.")
    else:
        st.write("Comprobantes cargados:")
        st.dataframe(df)

        api_key = "TEST_API_KEY"

        def consultar_proveedor(cuit):
            response = requests.get(
                f"https://api.cuitonline.com/constancia/{cuit}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if response.status_code == 200:
                return response.json().get('actividad', 'Sin datos')
            else:
                return "Error"

        df["Actividad"] = df["CUIT"].apply(consultar_proveedor)

        st.write("Comprobantes con actividad:")
        st.dataframe(df)

        output_path = os.path.join("outputs", "clasificados.xlsx")
        os.makedirs("outputs", exist_ok=True)
        df.to_excel(output_path, index=False)

        with open(output_path, "rb") as file:
            btn = st.download_button(
                label="📥 Descargar archivo clasificado",
                data=file,
                file_name="clasificados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
