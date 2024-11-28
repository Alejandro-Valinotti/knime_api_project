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

# Ruta de los workflows configurada desde variables de entorno o ruta por defecto
WORKFLOW_DIR = os.environ.get('WORKFLOW_DIR', './knime_api_project')

@app.route('/run-batch', methods=['POST'])
def run_batch():
    data = request.get_json()
    batch_name = data.get('batch_name')

    # Validar parámetro batch_name
    if not batch_name:
        logging.warning("El parámetro 'batch_name' no fue proporcionado.")
        print("ERROR: El parámetro 'batch_name' no fue proporcionado.")  # Debug en consola
        return jsonify({"status": "error", "message": "El parámetro 'batch_name' es obligatorio."}), 400

    # Ruta al archivo batch
    batch_file_path = os.path.join(WORKFLOW_DIR, f"{batch_name}.bat")

    # Debug: Verifica archivos disponibles en la carpeta
    try:
        archivos_disponibles = os.listdir(WORKFLOW_DIR)
        print(f"DEBUG: Archivos disponibles en {WORKFLOW_DIR}: {archivos_disponibles}")
    except Exception as e:
        print(f"DEBUG: Error al listar archivos en {WORKFLOW_DIR}: {str(e)}")
        return jsonify({"status": "error", "message": "No se puede acceder al directorio de workflows."}), 500

    # Verifica si el archivo batch existe
    if not os.path.isfile(batch_file_path):
        logging.error(f"No se encontró el archivo batch: {batch_file_path}")
        print(f"ERROR: No se encontró el archivo batch: {batch_file_path}")  # Debug en consola
        return jsonify({"status": "error", "message": f"El archivo batch '{batch_name}.bat' no se encontró."}), 404

    # Construir comando para ejecutar el batch
    command = f'"{batch_file_path}"'
    logging.info(f"Intentando ejecutar comando: {command}")
    print(f"INFO: Intentando ejecutar comando: {command}")  # Debug en consola

    try:
        # Ejecutar el batch
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        logging.info(f"Ejecución exitosa del archivo batch '{batch_name}'. Salida: {result.stdout}")
        print(f"SUCCESS: Ejecución exitosa del archivo batch '{batch_name}'.")  # Debug en consola
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        logging.error(f"Error en la ejecución del archivo batch '{batch_name}': {e.stderr}")
        print(f"ERROR: Error en la ejecución del archivo batch '{batch_name}': {e.stderr}")  # Debug en consola
        return jsonify({"status": "error", "output": e.stderr, "message": "Error ejecutando el archivo batch"}), 500
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        print(f"ERROR: Error inesperado: {str(e)}")  # Debug en consola
        return jsonify({"status": "error", "message": "Error inesperado al ejecutar el archivo batch"}), 500

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))  # Configura el puerto desde variables de entorno
    print(f"INFO: API corriendo en http://0.0.0.0:{PORT}")  # Debug en consola
    app.run(host='0.0.0.0', port=PORT)
