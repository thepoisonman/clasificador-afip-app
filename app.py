
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Clasificador AFIP App Refinado")

uploaded_file = st.file_uploader("Subí tu archivo Excel AFIP", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Vista previa del archivo cargado:", df.head())

    # Detectar la columna CUIT por posición (columna 7 -> index 6)
    if df.shape[1] >= 7:
        df.rename(columns={df.columns[6]: "CUIT", df.columns[7]: "Proveedor"}, inplace=True)
        df = df[df["CUIT"].astype(str).str.contains(r'\d')]

        st.write("Filtrado por CUIT válido:", df[["CUIT", "Proveedor"]])

        conceptos = []
        for i in range(len(df)):
            concepto_manual = st.text_input(
                f"Concepto para {df.iloc[i]['Proveedor']} ({df.iloc[i]['CUIT']})",
                key=f"concepto_{i}"
            )
            conceptos.append(concepto_manual)

        df["Concepto Refinado"] = conceptos

        # Botón de descarga
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("Descargar Excel Refinado", data=output.getvalue(), file_name="clasificado.xlsx")

    else:
        st.error("El archivo no contiene suficientes columnas para detectar CUIT y Proveedor.")
