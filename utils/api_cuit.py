
import requests

def consultar_cuit(cuit):
    api_key = "API_KEY_DE_PRUEBA"
    url = f"https://cuitonline.com/api/v1/cuit/{cuit}?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("actividad", "Sin información")
    return "Sin información"
