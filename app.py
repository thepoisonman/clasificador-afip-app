
import streamlit as st
import pandas as pd
import os

st.title("Clasificador AFIP App")

uploaded_file = st.file_uploader("Subí tu archivo de compras de AFIP (Excel)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Vista previa del archivo original:")
    st.dataframe(df)

    # Detectar CUIT y proveedor
    cuit_column, proveedor_column = None, None
    for col in df.columns:
        if df[col].astype(str).str.contains(r'\d{11}').any():
            cuit_column = col
        elif df[col].astype(str).str.contains(r'[a-zA-Z]').any() and "fecha" not in col.lower():
            proveedor_column = col

    if cuit_column and proveedor_column:
        df["Concepto Detectado"] = df[proveedor_column].apply(lambda x: "Servicios" if "TELECOM" in str(x).upper() else "Otros")

        st.subheader("Datos con concepto deducido:")
        st.dataframe(df)

        if not os.path.exists("outputs"):
            os.makedirs("outputs")
        df.to_excel("outputs/comprobantes_clasificados.xlsx", index=False)

        with open("outputs/comprobantes_clasificados.xlsx", "rb") as file:
            st.download_button("📥 Descargar Excel Clasificado", file, "comprobantes_clasificados.xlsx")

        st.subheader("Refinar conceptos:")
        conceptos_actualizados = []
        for i in range(len(df)):
            concepto_manual = st.text_input(f"Concepto para {df.iloc[i][proveedor_column]} (CUIT: {df.iloc[i][cuit_column]})",
                                            df.iloc[i]["Concepto Detectado"], key=f"concepto_{i}")
            conceptos_actualizados.append(concepto_manual)

        if st.button("Guardar conceptos refinados"):
            df["Concepto Refinado"] = conceptos_actualizados
            df.to_excel("outputs/comprobantes_refinados.xlsx", index=False)

            with open("outputs/comprobantes_refinados.xlsx", "rb") as file:
                st.download_button("📥 Descargar Excel Refinado", file, "comprobantes_refinados.xlsx")

    else:
        st.error("No se encontraron columnas válidas para CUIT y Proveedor. Verificá tu archivo.")
