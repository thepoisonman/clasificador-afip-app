
import streamlit as st
import pandas as pd
import requests
import io

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu archivo de compras AFIP (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, skiprows=7)  # ignorar encabezados iniciales

    # Verificar si hay una columna CUIT
    cuit_col = None
    for col in df.columns:
        if "CUIT" in col.upper():
            cuit_col = col
            break

    if cuit_col is None:
        st.error("No se encontró una columna que contenga 'CUIT'. Verificá el archivo.")
    else:
        df["CUIT"] = df[cuit_col]

        # Detectar conceptos automáticos según proveedor
        def detectar_concepto(proveedor):
            if pd.isna(proveedor):
                return "Desconocido"
            proveedor = proveedor.lower()
            if "super" in proveedor or "mercado" in proveedor:
                return "Alimentos"
            if "YPF" in proveedor or "AXION" in proveedor:
                return "Combustible"
            return "Otros"

        df["Concepto Detectado"] = df["Proveedor"].apply(detectar_concepto)

        # Corrección manual
        st.subheader("Correcciones manuales")
        conceptos = []
        for i in range(len(df)):
            proveedor = df.iloc[i]["Proveedor"]
            cuit = df.iloc[i]["CUIT"]
            concepto_detectado = df.iloc[i]["Concepto Detectado"]
            concepto_manual = st.text_input(
                f"{proveedor} ({cuit})", concepto_detectado, key=f"{i}"
            )
            conceptos.append(concepto_manual)

        df["Concepto Final"] = conceptos

        # Descargar archivo resultante
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Descargar Excel Clasificado",
            data=output,
            file_name="clasificado_afip.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
