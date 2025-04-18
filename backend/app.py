
import requests
from flask import Flask, request, jsonify

# Crear una aplicación Flask
app = Flask(__name__)

# API Key de CUIT Online (reemplaza con tu propia API Key)
API_KEY = "TU_API_KEY_AQUI"
CUIT_API_URL = "https://api.cuitonline.com.ar/api/v1/consultas"

# Ruta para consultar información del proveedor
@app.route('/consultar_proveedor', methods=['GET'])
def consultar_proveedor():
    cuit = request.args.get('cuit')  # Obtener CUIT de la consulta
    if not cuit:
        return jsonify({"error": "CUIT es requerido"}), 400

    # Parámetros de la consulta a la API de CUIT Online
    params = {
        "cuit": cuit,
        "api_key": API_KEY
    }

    try:
        response = requests.get(CUIT_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return jsonify(data), 200
        else:
            return jsonify({"error": "No se pudo obtener información del proveedor"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
