
import streamlit as st
import pandas as pd
from utils.api_cuit import consultar_cuit
from utils.classifier import clasificar_gasto

st.title('Clasificador de Comprobantes AFIP')

uploaded_file = st.file_uploader("Subí el archivo de comprobantes", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Vista previa:", df.head())

    # Buscar columnas candidatas a CUIT
    posibles_cuits = [col for col in df.columns if 'cuit' in col.lower() or 'documento' in col.lower()]

    if posibles_cuits:
        cuit_col = st.selectbox("Seleccioná la columna que contiene los CUIT:", posibles_cuits)
        df['Actividad'] = df[cuit_col].apply(consultar_cuit)
        df['Gasto'] = df.apply(clasificar_gasto, axis=1)

        st.write("Comprobantes clasificados:", df)

        output_path = f"data/export/comprobantes_clasificados.xlsx"
        df.to_excel(output_path, index=False)
        st.success(f"Archivo exportado: {output_path}")
    else:
        st.error("No se encontró ninguna columna que parezca contener CUITs.")
    