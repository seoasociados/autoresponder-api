from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

PROMPT_LARGO = """ 
x

 """

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def home():
    return "API de autorespuesta activa"

@app.route("/respuesta", methods=["POST"])
def responder():
    data = request.get_json()
    mensaje_usuario = data.get("mensaje", "")

    # Armar el prompt con tu prompt extenso + el mensaje del usuario
    prompt_total = f"{PROMPT_LARGO}\n\n[Usuario]: {mensaje_usuario}\n[Respuesta]:"

    try:
        completion = openai.chat.completions.create(
            model="gpt-4.1",  # puedes poner "gpt-4" si tienes acceso
            messages=[
                {"role": "system", "content": PROMPT_LARGO},
                {"role": "user", "content": mensaje_usuario}
            ],
            max_tokens=700,
            temperature=0.7
        )
        texto_respuesta = completion.choices[0].message.content.strip()
    except Exception as e:
        texto_respuesta = f"Error consultando OpenAI: {str(e)}"

   return jsonify({"replies": [ {"message": texto_respuesta} ] })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
