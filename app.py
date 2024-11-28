from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import logging

app = Flask(__name__)
CORS(app)

# Configuración de logs
logging.basicConfig(filename=os.path.join(os.getcwd(), "execution_logs.txt"), level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Carga de variables de entorno
KNIME_PATH = os.environ.get('KNIME_PATH', r"C:\Users\alejandro.valinotti\AppData\Local\Programs\KNIME\knime.exe")
# Configuración del directorio de workflows
WORKFLOW_DIR = os.environ.get('WORKFLOW_DIR', './knime_api_project')


@app.route('/run-batch', methods=['POST'])
def run_batch():
    # Obtener nombre del batch desde el cuerpo de la solicitud
    data = request.get_json()
    batch_name = data.get('batch_name')

    # Validar parámetro batch_name
    if not batch_name:
        logging.warning("El parámetro 'batch_name' no fue proporcionado.")
        print("ERROR: El parámetro 'batch_name' no fue proporcionado.")  # En consola
        return jsonify({"status": "error", "message": "El parámetro 'batch_name' es obligatorio."}), 400

    # Validar existencia del archivo batch
    batch_file_path = os.path.join(WORKFLOW_DIR, f"{batch_name}.bat")
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

@app.route('/env-vars', methods=['GET'])
def get_env_vars():
    """Endpoint de prueba para verificar las variables de entorno."""
    return jsonify({
        "KNIME_PATH": KNIME_PATH,
        "WORKFLOW_DIR": WORKFLOW_DIR
    })

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))  # Permitir configuración del puerto desde variables de entorno
    print(f"INFO: API corriendo en http://0.0.0.0:{PORT}")  # En consola
    app.run(host='0.0.0.0', port=PORT)
