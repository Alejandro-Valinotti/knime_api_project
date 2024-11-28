from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import logging

app = Flask(__name__)
CORS(app)  # Permite CORS para la comunicación con el frontend

# Configuración de logs en un archivo de texto en una ruta específica
logging.basicConfig(filename="C:\\knime_api_project\\execution_logs.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

@app.route('/run-workflow', methods=['POST'])
def run_workflow():
    data = request.get_json()
    batch_name = data.get('batch_name')
    logging.info(f"Solicitud de ejecución para: {batch_name}")

    # Ruta del archivo batch
    batch_file_path = os.path.join("C:\\knime_api_project", f"{batch_name}.bat")

    if not os.path.isfile(batch_file_path):
        logging.error(f"Archivo batch '{batch_name}.bat' no encontrado.")
        return jsonify({"status": "error", "message": f"El archivo batch '{batch_name}.bat' no se encontró."}), 404

    try:
        result = subprocess.run([batch_file_path], capture_output=True, text=True, check=True, shell=True)
        logging.info(f"Ejecución exitosa para el workflow '{batch_name}'")
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        logging.error(f"Error en la ejecución del workflow '{batch_name}': {e.stderr}")
        return jsonify({"status": "error", "output": e.stderr, "message": "Error ejecutando el archivo batch"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
