
def clasificar_gasto(row):
    actividad = row.get('Actividad', '')
    if "construcción" in actividad.lower():
        return "Obras"
    elif "servicio" in actividad.lower():
        return "Servicios"
    elif "alimento" in actividad.lower():
        return "Alimentos y Bebidas"
    else:
        return "Otros"
