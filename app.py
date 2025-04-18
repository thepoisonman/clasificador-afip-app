
import streamlit as st
import pandas as pd
import os

st.title("Clasificador AFIP App")

uploaded_file = st.file_uploader("Subí tu archivo Excel de compras AFIP", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Validación mínima
    if df.shape[1] < 8:
        st.error("El archivo debe tener al menos 8 columnas.")
    else:
        # Filtramos filas válidas
        df = df[df.iloc[:, 6].apply(lambda x: isinstance(x, (int, float, str)) and str(x).isdigit())]

        df['CUIT'] = df.iloc[:, 6]
        df['Proveedor'] = df.iloc[:, 7]

        conceptos_detectados = []
        with st.form("refinador_form"):
            for i, row in df.iterrows():
                proveedor = row['Proveedor']
                cuit = row['CUIT']
                valor_detectado = "Sin clasificar"
                concepto_manual = st.text_input(
                    f"Concepto para {proveedor} (CUIT {cuit})",
                    valor_detectado,
                    key=f"concepto_{i}"
                )
                conceptos_detectados.append(concepto_manual)

            submitted = st.form_submit_button("Guardar clasificaciones")

        if submitted:
            df['Concepto Detectado'] = conceptos_detectados

            # Crear carpeta outputs
            os.makedirs("outputs", exist_ok=True)
            output_path = os.path.join("outputs", "clasificados.xlsx")
            df.to_excel(output_path, index=False)

            st.success(f"Archivo guardado en {output_path}")
