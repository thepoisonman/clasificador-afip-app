
import streamlit as st
import pandas as pd
import os
import re

# Crear carpeta outputs si no existe
if not os.path.exists("outputs"):
    os.makedirs("outputs")

st.title("Clasificador de Facturas AFIP")

uploaded_file = st.file_uploader("Subí tu Excel de compras AFIP", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Detección dinámica de CUIT y Proveedor
    cuit_pattern = re.compile(r'\b(20|23|24|27|30|33|34)\d{9}\b')
    cuit_col, prov_col = None, None

    for col in df.columns:
        if df[col].astype(str).str.contains(cuit_pattern).any():
            cuit_col = col
        elif df[col].astype(str).str.contains('[A-Za-z]', regex=True).any() and prov_col is None:
            prov_col = col

    if not cuit_col or not prov_col:
        st.error("No se encontraron columnas válidas de CUIT y Proveedor. Verificá tu archivo.")
    else:
        # Concepto automático según proveedor
        df["Concepto Detectado"] = df[prov_col].apply(lambda x: "Servicios" if "INTERNET" in str(x).upper() else "Otros")

        st.write("📄 Vista previa:")
        st.dataframe(df[[prov_col, cuit_col, "Concepto Detectado"]])

        output_path = os.path.join("outputs", "clasificado.xlsx")
        df.to_excel(output_path, index=False)
        st.success("Clasificación generada.")

        with open(output_path, "rb") as f:
            st.download_button("📥 Descargar Excel Clasificado", f, file_name="clasificado.xlsx")

        # Refinamiento manual
        st.subheader("🔧 Refinar conceptos")
        for i in range(len(df)):
            concepto_manual = st.text_input(f"{df.iloc[i][prov_col]} ({df.iloc[i][cuit_col]})",
                                            df.iloc[i]["Concepto Detectado"], key=f"input_{i}")
            df.at[i, "Concepto Detectado"] = concepto_manual

        output_path_ref = os.path.join("outputs", "clasificado_refinado.xlsx")
        df.to_excel(output_path_ref, index=False)

        with open(output_path_ref, "rb") as f:
            st.download_button("📥 Descargar Excel Refinado", f, file_name="clasificado_refinado.xlsx")
