from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API de autorespuesta activa"

@app.route("/respuesta", methods=["POST"])
def responder():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    
    # Aquí defines la respuesta automática
    if "hola" in mensaje.lower():
        respuesta = "Holaa ☺️ gracias x escribirme jejeje"
    else:
        respuesta = "Gracias x tu mensajito, en breve te respondo 😇"
    
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
