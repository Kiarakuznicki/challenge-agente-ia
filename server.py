from flask import Flask, request, jsonify, send_from_directory

from app import obtener_vectorstore
from src.agent import responder_pregunta

app = Flask(__name__, static_folder="static", static_url_path="")

print("Iniciando servidor: cargando/indexando la base de conocimiento...")
db = obtener_vectorstore()
print("Listo. Base de conocimiento cargada.")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/preguntar", methods=["POST"])
def preguntar():
    data = request.get_json(silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()

    if not pregunta:
        return jsonify({"error": "La pregunta no puede estar vacía"}), 400

    try:
        resultado = responder_pregunta(pregunta, db)
    except Exception as e:
        return jsonify({"error": f"Error al procesar la pregunta: {e}"}), 500

    fuentes = sorted({
        f"{d.metadata.get('source', 'documento')} (pág. {d.metadata.get('page', '?')})"
        for d in resultado["fuentes"]
    })

    return jsonify({"respuesta": resultado["respuesta"], "fuentes": fuentes})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=False)