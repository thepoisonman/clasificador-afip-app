
import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Clasificador de Compras AFIP")

# Subida del archivo
uploaded_file = st.file_uploader("Subí tu archivo de compras (Excel)", type=["xlsx"])

if uploaded_file is not None:
    # Leer el archivo
    df = pd.read_excel(uploaded_file, sheet_name='Sheet1', skiprows=1)
    
    # Renombrar columnas para trabajar más cómodo
    df.columns = ['Fecha', 'Tipo', 'Punto de Venta', 'Número Desde', 'Número Hasta', 'Tipo Doc. Vendedor',
                  'Nro. Doc. Vendedor', 'Denominación Vendedor', 'Tipo Cambio', 'Moneda', 'Neto Gravado',
                  'No Gravado', 'Exento', 'IVA', 'Total']
    
    # Propuesta inicial de categoría (placeholder)
    def sugerir_categoria(row):
        if 'AUTOPISTA' in row['Denominación Vendedor'].upper():
            return 'Transporte'
        elif 'ALQUILER' in row['Denominación Vendedor'].upper():
            return 'Alquiler'
        elif 'SERVICIO' in row['Denominación Vendedor'].upper():
            return 'Servicios'
        else:
            return 'Otros'

    df['Categoría'] = df.apply(sugerir_categoria, axis=1)

    # Mostrar tabla editable
    st.write("### Clasificación de Compras")
    for idx, row in df.iterrows():
        nueva_categoria = st.selectbox(
            f"Categoría para {row['Denominación Vendedor']}",
            ('Transporte', 'Alquiler', 'Servicios', 'Otros'),
            index=['Transporte', 'Alquiler', 'Servicios', 'Otros'].index(row['Categoría']),
            key=f"categoria_{idx}"
        )
        df.at[idx, 'Categoría'] = nueva_categoria

    # Descargar archivo
    st.write("### Descargar archivo clasificado")
    output_file = df.to_excel(index=False)
    st.download_button(
        label="📥 Descargar Excel con categorías",
        data=output_file,
        file_name="compras_clasificadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Por favor, subí un archivo para comenzar.")
