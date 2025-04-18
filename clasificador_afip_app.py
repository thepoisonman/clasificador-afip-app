
import pandas as pd
import streamlit as st
from config import CUIT_API_KEY

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí el archivo de comprobantes AFIP (.xlsx)", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if 'CUIT' not in df.columns:
        st.error("El archivo no tiene columna 'CUIT'. Verificá el formato.")
    else:
        st.write("Comprobantes cargados:")
        st.dataframe(df)

        # Solo muestra la API key para debugging (vacía)
        st.write("CUIT API KEY configurada:", CUIT_API_KEY if CUIT_API_KEY else "No configurada")

        # Simula asignación de categorías
        df["Categoría"] = "Sin definir"

        # Permitir asignación manual
        for idx, row in df.iterrows():
            nueva_categoria = st.selectbox(f"Categoría para {row['CUIT']}:", 
                                           ['Servicios', 'Productos', 'Inmuebles', 'Otros'], 
                                           key=idx)
            df.at[idx, "Categoría"] = nueva_categoria

        st.write("Resultado final:")
        st.dataframe(df)

        # Guardar resultado
        output_path = "/mnt/data/comprobantes_clasificados.xlsx"
        df.to_excel(output_path, index=False)
        st.success("Archivo clasificado generado.")
        st.download_button("Descargar archivo clasificado", output_path)
