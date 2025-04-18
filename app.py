
import streamlit as st
import pandas as pd
import numpy as np
import re
import os

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu archivo Excel de comprobantes AFIP", type=["xlsx"])

def detectar_columnas(df):
    cuit_col, proveedor_col = None, None
    for col in df.columns:
        if df[col].astype(str).str.contains(r'\b\d{11}\b').any():
            cuit_col = col
        if df[col].astype(str).str.contains(r'[^\d]{3,}').any():
            proveedor_col = col
    return cuit_col, proveedor_col

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    cuit_col, proveedor_col = detectar_columnas(df)

    if not cuit_col or not proveedor_col:
        st.error("No se detectaron columnas válidas para CUIT y Proveedor.")
    else:
        def deducir_concepto(proveedor):
            proveedor = str(proveedor).lower()
            if "super" in proveedor or "carrefour" in proveedor:
                return "Supermercado"
            elif "shell" in proveedor or "ypf" in proveedor:
                return "Combustible"
            elif "farmacia" in proveedor:
                return "Farmacia"
            else:
                return "Otros"

        df["Concepto Detectado"] = df[proveedor_col].apply(deducir_concepto)

        st.subheader("Vista previa con conceptos deducidos")
        st.dataframe(df[[proveedor_col, cuit_col, "Concepto Detectado"]])

        output_path = "outputs/comprobantes_deducidos.xlsx"
        os.makedirs("outputs", exist_ok=True)
        df.to_excel(output_path, index=False)
        with open(output_path, "rb") as f:
            st.download_button("📥 Descargar Excel con conceptos deducidos", f, file_name="comprobantes_deducidos.xlsx")

        st.subheader("Refinar conceptos manualmente")
        conceptos_refinados = []
        for i in range(len(df)):
            concepto_manual = st.text_input(f"Concepto para {df.iloc[i][proveedor_col]} ({df.iloc[i][cuit_col]})", df.iloc[i]["Concepto Detectado"], key=f"{i}")
            conceptos_refinados.append(concepto_manual)

        if st.button("Guardar Excel refinado"):
            df["Concepto Refinado"] = conceptos_refinados
            refined_path = "outputs/comprobantes_refinados.xlsx"
            df.to_excel(refined_path, index=False)
            with open(refined_path, "rb") as f:
                st.download_button("📥 Descargar Excel refinado", f, file_name="comprobantes_refinados.xlsx")
