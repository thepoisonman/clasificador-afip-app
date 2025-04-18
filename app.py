
import streamlit as st
import pandas as pd
import os

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí el archivo de comprobantes", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Asumiendo columnas: 7 = CUIT, 8 = Proveedor
    cuit_col = df.columns[6]
    proveedor_col = df.columns[7]

    st.write("Vista previa del archivo:")
    st.dataframe(df.head())

    # Simulación de búsqueda por CUIT
    conceptos_detectados = []
    for i in range(len(df)):
        cuit = df.iloc[i, 6]
        proveedor = df.iloc[i, 7]
        concepto_detectado = "Gastos Generales"  # valor dummy
        conceptos_detectados.append(concepto_detectado)

    df["Concepto Detectado"] = conceptos_detectados

    st.write("Resultado con conceptos detectados:")
    st.dataframe(df)

    st.write("Refiná los conceptos manualmente:")
    for i in range(len(df)):
        concepto_manual = st.text_input(
            f"Concepto para {df.iloc[i][proveedor_col]} ({df.iloc[i][cuit_col]})",
            df.iloc[i]["Concepto Detectado"],
            key=f"concepto_{i}"
        )
        df.at[i, "Concepto Detectado"] = concepto_manual

    # Guardado
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    output_path = os.path.join("outputs", "resultado_comprobantes.xlsx")
    df.to_excel(output_path, index=False)

    st.success(f"Archivo guardado en {output_path}")
    with open(output_path, "rb") as file:
        st.download_button("Descargar archivo procesado", file, file_name="resultado_comprobantes.xlsx")
