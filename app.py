
import streamlit as st
import pandas as pd
import io

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu Excel de Comprobantes AFIP", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    try:
        # Renombrar columnas por posición
        df.columns.values[6] = 'CUIT'
        df.columns.values[7] = 'Proveedor'

        # Filtrar solo las filas con CUIT válidos (11 dígitos numéricos)
        df = df[df['CUIT'].astype(str).str.fullmatch(r'\d{11}')]

        # Clasificación automática simple
        df["Concepto Detectado"] = df["Proveedor"].apply(lambda x: "Servicios" if "S.A." in str(x) else "Bienes")

        st.subheader("Vista previa de los comprobantes filtrados")
        st.dataframe(df)

        # Guardar en memoria
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        # Botón de descarga
        st.download_button(
            label="📥 Descargar Excel refinado",
            data=output,
            file_name="comprobantes_refinados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
