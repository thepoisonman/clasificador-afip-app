
import streamlit as st
import pandas as pd
import os
import json

# Crear carpeta outputs si no existe
os.makedirs("outputs", exist_ok=True)

# Cargar memoria de refinamientos si existe
if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        memory = json.load(f)
else:
    memory = {}

st.title("Clasificador de Compras AFIP")

uploaded_file = st.file_uploader("Subí tu Excel de compras AFIP", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Detectar columna CUIT
    cuit_col = next((col for col in df.columns if "CUIT" in col.upper()), None)
    proveedor_col = next((col for col in df.columns if "PROVEEDOR" in col.upper() or "EMISOR" in col.upper()), None)

    if not cuit_col or not proveedor_col:
        st.error("No se detectaron correctamente las columnas de CUIT y Proveedor.")
    else:
        conceptos = []
        for index, row in df.iterrows():
            cuit = str(row[cuit_col])
            proveedor = str(row[proveedor_col])

            # Usar memoria si existe
            concepto = memory.get(cuit, "Otros")
            conceptos.append(concepto)

        df["Concepto"] = conceptos

        st.success("Clasificación generada.")
        st.dataframe(df)

        df.to_excel("outputs/clasificado.xlsx", index=False)
        with open("outputs/clasificado.xlsx", "rb") as f:
            st.download_button("📥 Descargar Excel Clasificado", f, file_name="clasificado.xlsx")

        st.markdown("### 🔧 Refinar conceptos")

        nuevos_conceptos = {}
        for index, row in df.iterrows():
            proveedor = str(row[proveedor_col])
            cuit = str(row[cuit_col])
            concepto_actual = row["Concepto"]

            nuevo = st.text_input(f"{proveedor} ({cuit})", concepto_actual, key=index)
            nuevos_conceptos[cuit] = nuevo

        if st.button("Guardar y descargar refinado"):
            df["Concepto"] = df[cuit_col].map(nuevos_conceptos)
            df.to_excel("outputs/refinado.xlsx", index=False)
            with open("outputs/refinado.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel Refinado", f, file_name="refinado.xlsx")

            memory.update(nuevos_conceptos)
            with open("memory.json", "w") as f:
                json.dump(memory, f)

