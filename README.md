
# Clasificador de Compras AFIP

Aplicación web para clasificar comprobantes de compras de AFIP según proveedor.

## Cómo usar

1. Subí un archivo de compras descargado desde AFIP (formato Excel).
2. La app sugerirá una categoría para cada factura.
3. Podés ajustar manualmente las categorías desde la app.
4. Descargá el Excel con las categorías corregidas.

## Instalación

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Cloud

1. Subí estos archivos a un repositorio de GitHub.
2. Conectá tu cuenta en [https://streamlit.io/cloud](https://streamlit.io/cloud).
3. Creá una nueva app desde tu repositorio.
4. ¡Listo!
