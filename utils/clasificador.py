
def clasificar_gastos(proveedor, cuit, memoria):
    key = f"{cuit}|{proveedor}"
    if key in memoria:
        return memoria[key]

    proveedor_lower = str(proveedor).lower()
    if 'mercado' in proveedor_lower:
        return "Compras MercadoLibre"
    elif 'farmacia' in proveedor_lower:
        return "Gastos Farmacia"
    elif 'super' in proveedor_lower:
        return "Supermercado"
    elif 'hotel' in proveedor_lower:
        return "Gastos de Viaje"
    else:
        return "Otros"
