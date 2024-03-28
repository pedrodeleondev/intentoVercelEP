from flask import Flask, render_template, request, jsonify
from hpScrapy import iniciarCodigo
import os

app = Flask(__name__)

# Variable para almacenar el archivo JSON
uploaded_json = None

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
  global uploaded_json

  # Verifica si se envió un archivo JSON
  if 'json_file' in request.files:
    json_file = request.files['json_file']

    # Guarda el archivo en una ubicación temporal
    file_path = os.path.join(json_file.filename)
    json_file.save(file_path)

    # Almacena el archivo en la variable
    uploaded_json = file_path

    # Inicia el código con el archivo JSON
    result = iniciarCodigo(uploaded_json)

    # Devuelve una respuesta en formato JSON
    return jsonify(result)

  return "No se proporcionó un archivo JSON."

if __name__ == '__main__':
  app.run(debug=True)