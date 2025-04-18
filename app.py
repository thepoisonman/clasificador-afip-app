
import streamlit as st
import pandas as pd
import requests
import os

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu archivo de comprobantes AFIP (Excel)", type=["xlsx"])

if uploaded_file is not None:
    # Leer Excel
    df = pd.read_excel(uploaded_file)
    st.write("### Vista previa de los datos")
    st.dataframe(df.head())

    # Detectar columnas candidatas a CUIT
    posibles_cuit = [col for col in df.columns if 'cuit' in col.lower() or 'documento' in col.lower()]
    if not posibles_cuit:
        st.error("No se encontró ninguna columna que parezca contener CUITs.")
        st.stop()

    cuit_col = st.selectbox("Seleccioná la columna que contiene el CUIT:", posibles_cuit)

    # Consulta a CUIT Online API
    api_key = "APIKEY_DE_PRUEBA_123456"
    api_url = "https://api.cuitonline.com/v1/constancia"

    def consultar_cuit_online(cuit):
        try:
            resp = requests.get(f"{api_url}/{cuit}?apikey={api_key}")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("actividad_principal", "Sin datos")
        except:
            pass
        return "Error consulta"

    st.write("### Consultando actividad AFIP...")
    df["Actividad AFIP"] = df[cuit_col].astype(str).apply(consultar_cuit_online)

    # Clasificación manual asistida
    st.write("### Refinar conceptos manualmente si es necesario")
    conceptos = []
    for idx, row in df.iterrows():
        default = row["Actividad AFIP"]
        opcion = st.selectbox(
            f"Concepto para {row.get('Proveedor', row.get(cuit_col))}",
            ["Servicios", "Bienes", "Transporte", "Alquiler", "Otros"],
            index=0,
            key=f"concepto_{idx}"
        )
        conceptos.append(opcion)
    df["Concepto"] = conceptos

    # Mostrar resultado final
    st.write("### Resultado final")
    st.dataframe(df)

    # Guardar y descargar
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "comprobantes_clasificados.xlsx")
    df.to_excel(output_path, index=False)

    with open(output_path, "rb") as f:
        st.download_button(
            "📥 Descargar archivo clasificado",
            data=f,
            file_name="comprobantes_clasificados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
