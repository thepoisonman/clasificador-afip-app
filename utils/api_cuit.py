
def consultar_cuit(cuit):
    # Simulación de consulta a API pública
    if str(cuit).startswith("30"):
        return "Servicios"
    elif str(cuit).startswith("20"):
        return "Bienes"
    else:
        return "Otros"
    