from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import logging

app = Flask(__name__)
CORS(app)

# Configuración de logs
logging.basicConfig(filename="C:\\knime_api_project\\execution_logs.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Ruta del directorio donde se encuentran los archivos batch
BATCH_DIR = r"C:\knime_api_project"

@app.route('/run-batch', methods=['POST'])
def run_batch():
    data = request.get_json()
    batch_name = data.get('batch_name')

    # Validar parámetro batch_name
    if not batch_name:
        logging.warning("El parámetro 'batch_name' no fue proporcionado.")
        print("ERROR: El parámetro 'batch_name' no fue proporcionado.")  # En consola
        return jsonify({"status": "error", "message": "El parámetro 'batch_name' es obligatorio."}), 400

    # Validar existencia del archivo batch
    batch_file_path = os.path.join(BATCH_DIR, f"{batch_name}.bat")
    if not os.path.isfile(batch_file_path):
        logging.error(f"No se encontró el archivo batch: {batch_file_path}")
        print(f"ERROR: No se encontró el archivo batch: {batch_file_path}")  # En consola
        return jsonify({"status": "error", "message": f"El archivo batch '{batch_name}.bat' no se encontró."}), 404

    # Construir el comando para ejecutar el batch
    command = f'"{batch_file_path}"'  # Envolver el path del batch en comillas dobles

    logging.info(f"Intentando ejecutar comando: {command}")
    print(f"INFO: Intentando ejecutar comando: {command}")  # En consola

    try:
        # Ejecutar el comando
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        logging.info(f"Ejecución exitosa del archivo batch '{batch_name}'. Salida: {result.stdout}")
        print(f"SUCCESS: Ejecución exitosa del archivo batch '{batch_name}'.")  # En consola
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        logging.error(f"Error en la ejecución del archivo batch '{batch_name}': {e.stderr}")
        print(f"ERROR: Error en la ejecución del archivo batch '{batch_name}': {e.stderr}")  # En consola
        return jsonify({"status": "error", "output": e.stderr, "message": "Error ejecutando el archivo batch"}), 500
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        print(f"ERROR: Error inesperado: {str(e)}")  # En consola
        return jsonify({"status": "error", "message": "Error inesperado al ejecutar el archivo batch"}), 500

if __name__ == '__main__':
    print("INFO: API corriendo en http://0.0.0.0:5000")  # En consola
    app.run(host='0.0.0.0', port=5000)
