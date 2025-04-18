
def clasificar_gasto(row):
    actividad = row['Actividad']
    if actividad == "Servicios":
        return "Honorarios"
    elif actividad == "Bienes":
        return "Mercaderías"
    else:
        return "Otros gastos"
    