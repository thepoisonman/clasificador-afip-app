
import pandas as pd
import streamlit as st
import os

# Subir archivo
uploaded_file = st.file_uploader("Subí tu archivo de comprobantes", type=["xlsx"])

if uploaded_file is not None:
    # Leer sin encabezado para buscarlo manualmente
    df_raw = pd.read_excel(uploaded_file, header=None)

    # Buscar la fila donde está la cabecera real (buscando la palabra 'CUIT')
    header_row = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains('CUIT').any(), axis=1)].index[0]

    # Leer de nuevo ahora sí con el header correcto
    df = pd.read_excel(uploaded_file, header=header_row)

    # Filtrar filas inválidas o con encabezados intermedios
    df = df[df['CUIT'].notna() & df['CUIT'].astype(str).str.contains('\\d')]

    # Detectar conceptos (solo como ejemplo)
    df["Concepto Detectado"] = "A clasificar"

    st.write("Comprobantes cargados:")
    st.dataframe(df)

    # Corrección manual con claves únicas
    for i in range(len(df)):
        proveedor = df.iloc[i]['Proveedor']
        cuit = df.iloc[i]['CUIT']
        concepto_detectado = df.iloc[i]['Concepto Detectado']
        concepto_manual = st.text_input(
            f"{proveedor} ({cuit})",
            concepto_detectado,
            key=f"concepto_{i}"
        )
        df.at[i, 'Concepto Detectado'] = concepto_manual

    # Guardar resultado
    output_path = 'outputs/comprobantes_clasificados.xlsx'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)

    with open(output_path, "rb") as file:
        st.download_button("📥 Descargar Excel Clasificado", file, file_name="clasificados.xlsx")
