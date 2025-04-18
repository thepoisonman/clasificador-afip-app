
import streamlit as st
import pandas as pd
import os
import json
import re
import requests

# Crear carpetas necesarias
os.makedirs('outputs', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Cargar memoria
if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        memoria = json.load(f)
else:
    memoria = {}

st.title("Clasificador de Comprobantes AFIP")

uploaded_file = st.file_uploader("Subí tu Excel de comprobantes AFIP", type=["xlsx"])
if uploaded_file:
    # Cargar el archivo y usar la segunda fila como encabezado
    df = pd.read_excel(uploaded_file, header=1)

    # Mostrar el preview de las primeras filas para validación
    st.subheader("Preview de los datos cargados")
    st.dataframe(df.head())

    # Proceso de detección avanzada de CUIT/DNI y Proveedor
    def es_cuit_o_dni(value):
        # Validar si es un CUIT (11 dígitos) o un DNI (7-8 dígitos)
        value = str(value).strip()
        return len(value) >= 7 and len(value) <= 11 and value.isdigit()

    cuit_col = None
    proveedor_col = None

    # Detección de columnas de CUIT/DNI y Proveedor
    for col in df.columns:
        if df[col].apply(es_cuit_o_dni).sum() > 0:
            cuit_col = col
        elif df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, str) and not es_cuit_o_dni(x)).sum() > 0:
            proveedor_col = col

    # Mostrar registros de depuración para identificar las columnas detectadas
    st.subheader("Registros de depuración de las columnas detectadas")
    st.write(f"Columna de CUIT detectada: {cuit_col}")
    st.write(f"Columna de Proveedor detectada: {proveedor_col}")

    # Preguntar al usuario si las columnas están correctamente asignadas
    columnas_correctas = st.radio("¿Están correctas las columnas de CUIT y Proveedor?", ('Sí', 'No'))

    if columnas_correctas == 'No':
        # Permitir que el usuario seleccione manualmente las columnas de CUIT y Proveedor
        st.subheader("Seleccione manualmente las columnas de CUIT y Proveedor")
        cuit_col = st.selectbox("Seleccione la columna de CUIT", df.columns, key="cuit_column")
        proveedor_col = st.selectbox("Seleccione la columna de Proveedor", df.columns, key="proveedor_column")

        # Mostrar botón de confirmación para guardar la corrección
        if st.button("Confirmar selección de columnas"):
            # Guardar la corrección del usuario en memoria para futuros usos
            if cuit_col and proveedor_col:
                memoria['ultimo_cuit_col'] = cuit_col
                memoria['ultimo_proveedor_col'] = proveedor_col
                st.success("Corrección guardada en la memoria.")

    # Renombrar las columnas para mejorar la visualización
    if len(df.columns) == 9:
        df.columns = ['Fecha', 'Tipo', 'Punto de Venta', 'Número Desde', 'Número Hasta', 'Tipo Doc. Vendedor', 'CUIT', 'Proveedor', 'Concepto Detectado']
    else:
        st.warning("El archivo no tiene el número exacto de columnas esperado, pero se continuará con el procesamiento.")

    if cuit_col and proveedor_col:
        df['CUIT'] = df[cuit_col]
        df['Proveedor'] = df[proveedor_col]

        # Lógica mejorada de detección de conceptos con consulta API
        def obtener_informacion_proveedor(cuit):
            # Obtenemos la información del proveedor a partir de su CUIT
            params = {
                "cuit": cuit,  # CUIT del proveedor
                "api_key": "TU_API_KEY_AQUI"  # Asegúrate de agregar tu API Key
            }
            
            try:
                response = requests.get("https://api.cuitonline.com.ar/api/v1/consultas", params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    st.warning(f"No se pudo obtener información para el CUIT {cuit}")
                    return None
            except Exception as e:
                st.error(f"Error al consultar la API: {e}")
                return None

        # Mejora la precisión de la detección de concepto usando la información del proveedor
        def mejorar_precision_concepto(row):
            proveedor = str(row['Proveedor']).lower()
            cuit = str(row['CUIT']).strip()

            # Consultar la API para obtener más detalles del proveedor
            proveedor_info = obtener_informacion_proveedor(cuit)

            if proveedor_info:
                # Si la API devuelve información, usamos la actividad para mejorar la precisión
                actividad = proveedor_info.get('actividad', '').lower()
                if 'mercadolibre' in proveedor:
                    return 'Venta MercadoLibre'
                elif 'sushi' in proveedor:
                    return 'Comida Rápida'
                elif 'tecnología' in actividad:
                    return 'Electrónica'
                elif 'alimentación' in actividad:
                    return 'Comida y Bebidas'
                elif 'consultoría' in actividad:
                    return 'Servicios de Consultoría'
                else:
                    return 'Otros'  # Concepto aún muy general
            else:
                # Si no encontramos información en la API, volvemos a la lógica básica
                if 'mercadolibre' in proveedor:
                    return 'Venta MercadoLibre'
                elif 'sushi' in proveedor:
                    return 'Comida Rápida'
                elif 'tecnología' in proveedor:
                    return 'Electrónica'
                else:
                    return 'Otros'  # Concepto aún muy general

        # Aplicar la detección de concepto mejorada
        df['Concepto Detectado'] = df.apply(mejorar_precision_concepto, axis=1)

        st.dataframe(df)

        # Crear archivo Excel clasificado
        output_file = f"outputs/comprobantes_clasificados.xlsx"
        df.to_excel(output_file, index=False)
        st.success(f"Archivo clasificado generado: {output_file}")

        # Proveer un enlace para descargar el archivo clasificado
        st.download_button(label="Descargar Excel Clasificado", data=open(output_file, "rb").read(), file_name="comprobantes_clasificados.xlsx")

        st.subheader("Refinar conceptos manualmente")
        for i in range(len(df)):
            # Cambiar la forma en que se presenta el Proveedor en la interfaz de refinamiento
            concepto_manual = st.text_input(f"Concepto para {df.iloc[i]['Proveedor']} ({df.iloc[i]['CUIT']})",
                                            df.iloc[i]["Concepto Detectado"],
                                            key=f"concepto_{i}")
            df.at[i, "Concepto Detectado"] = concepto_manual
            memoria[df.iloc[i]['CUIT']] = concepto_manual

        refined_output = f"outputs/comprobantes_refinados.xlsx"
        df.to_excel(refined_output, index=False)
        st.success(f"Archivo refinado generado: {refined_output}")

        # Proveer un enlace para descargar el archivo refinado
        st.download_button(label="Descargar Excel Refinado", data=open(refined_output, "rb").read(), file_name="comprobantes_refinados.xlsx")

        # Validar y asegurar que los valores en 'memoria' sean serializables
        memoria_validada = {str(key): str(value) if isinstance(value, (int, float, str)) else None for key, value in memoria.items()}

        with open("memory.json", "w") as f:
            json.dump(memoria_validada, f, indent=4)

    else:
        st.error("No se detectaron correctamente las columnas de CUIT y Proveedor.")
