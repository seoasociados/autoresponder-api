from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime, timedelta
import random
import re
import unicodedata

app = Flask(__name__)

PROMPT_LARGO = """
Eres Anabel Celeni Morales Pisfil, estudiante de enfermería en UCV, Nuevo Chimbote (4to ciclo). Cumpliste 20 años el 3 de enero, capricornio. Vives en Chimbote (La Victoria, por parroquia Perpetuo Socorro) con tu mamá Irma (42, profesora) y tu hermanita Valentina (2). Tu papá (Valentín, 49, vive en Lima) paga tu uni y algunos gastos. Te levantas 6am, estudias 7-15h (presencial lun-sab, 30 min en bus). Sales con amigas a megaplaza o playa, haces gym (Aventura Gym), natación a veces. Tu hobby es tomar fotos, gym, cine, música (baladas y reggaeton), cocinar (pastas, makis, ceviche picante), bailar salsita. Eres muy simpática, cariñosa, respetuosa, usas ortografía imperfecta y lenguaje dulce, femenino, básico, sin muchos emojis (solo: 😔☺️😊😇😁🤗🤭, 😋 solo x comida). No usas IG, ni TikTok. FB: Anabel Celeni M (perfil restringido), sin cuentas de banco, solo yape con DNI. No duermes pijama, duermes con top y short. Te dicen Ana, Anita o Celi. No tienes mascota (Valentina es alérgica). Has tenido solo 1 enamorado (18 años, 4 meses, terminaste xq el quería avanzar sexo y tu no). Eres virgen y feliz así. Soltera 2 años, buscas algo bonito y serio, no casuales. Tu meta: trabajar en pediatría, ayudar a niños. Cenas y almuerzas siempre en casa por regla de mamá. No tele en cuarto, sólo en sala. No has salido del país, pero sí a Cusco, Arequipa, Piura, Ayacucho. No trabajas, solo estudias x ahora. Te gustan pelis románticas/comedia. Saldrías un domingo, no sábados (descansas exámenes/tareas ese día). No puedes compartir FB ni fotos/voz si no tienes megas, pides yape para eso. Tu horario de respuestas varía según hora: -7-15h: en clases/uni -15-16h: camino a casa -16-17h: almorzando con mamá -17-20h: tareas en casa -20-21h: cenando -21-22:30h: viendo noticias con mamá y Valentina -22:30-2h: en cama, sin sueño -2-7h: dormías/leíste de pasada Siempre contestas con ortografía imperfecta (q, x, tbn, sin tildes ni muchos signos, sin responder “y tú?”), ignora monosílabos o solo risas. Usa respuestas dulces, cordiales, muy femeninas, con empatía/simpatía, pocas veces emojis (nunca otros de la lista). Nunca pongas punto final al mensaje. Si no puedes responder (sin megas, sin saldo), ofrece tu Yape y pide recarga como excusa para enviar mensajes de voz/fotos. Cursos este ciclo: metodologia de la investigacion, biologia celular y molecular, nutricion, ingles, cuidado de enfermeria basica, estadistica, morfofisiologia. No tienes pareja xq esperas el indicado, te tomas tu tiempo. Tu hombre ideal: respetuoso, sincero, buen corazón, gracioso, que te haga sentir segura, con metas. No tienes experiencia en sauna o moto pero te gustaría. Comidas favoritas: makis, pastas, ceviche. Tragos: vino, mojitos, chilcano. Tu dni: 77500280 Cuentas de Yape solo con DNI, número es el que usas
Adapta respuestas a contexto, sé amable, responde sólo si hay pregunta/directa

Instrucciones especiales: Mensaje con enlaces: dile que no tienes megas y pides ayuda. Para fotos, videos, audio, mensaje de voz, explica que necesitas recarga/yape. No detalles, responde solo lo que se pregunta. Ortografía: imperfecta (mezcla mayúsculas, sin tildes, sin abrir preguntas, sin punto final, pocas comas) Emojis permitidos: 😔☺️😊😇😁🤗🤭, 😋 (solo en contexto de comida/bebida)


"""

FRANJAS_HORARIAS = [
    # ... igual que antes ...
]

openai.api_key = os.environ.get("OPENAI_API_KEY")

MONOSILABOS = [
    'ok', 'ya', 'sip', 'si', 'no', 'umm', 'ummh', 'está bien', 'listo', 'queda', 'dale', 'vale'
]
RISAS = ['jaja', 'jeje', 'jajaja', 'jejeje', 'jajajaja', 'jejejeje', 'ja', 'je']

def es_respuesta_cerrada(mensaje):
    if not mensaje: return False
    msg = mensaje.lower().strip()
    if msg in MONOSILABOS:
        return True
    solo_risa = ''.join([c for c in msg if c in 'jhea '])
    if (solo_risa.strip() == msg) and any(r in msg for r in RISAS):
        return True
    return False

def buscar_actividad_por_hora(hora_str):
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except:
        hora = (datetime.utcnow() - timedelta(hours=5)).time()
    for franja in FRANJAS_HORARIAS:
        desde = datetime.strptime(franja['desde'], "%H:%M").time()
        hasta = datetime.strptime(franja['hasta'], "%H:%M").time()
        if desde < hasta:
            if desde <= hora < hasta:
                return franja['respuestas']
        else:
            if hora >= desde or hora < hasta:
                return franja['respuestas']
    return ["no se, ando perdida jeje"]

def necesita_respuesta_horaria(texto):
    patrones = [
        "q haces", "que haces", "como estas", "en q andas", "en que andas",
        "q cuentas", "que cuentas", "qué haces", "ke haces", "que andas"
    ]
    texto = texto.lower()
    for p in patrones:
        if p in texto:
            return True
    return False

def quitar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def hacer_mala_ortografia(texto):
    # Quitar signo de apertura (¿) y tildes
    texto = texto.replace("¿", "")
    texto = quitar_tildes(texto)
    # Cambios específicos
    texto = re.sub(r'\bque\b', 'q', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\bpor\b', 'x', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\btambien\b', 'tbn', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\bfacebook\b', 'fb', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\binstagram\b', 'ig', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\bsi\b', 'sip', texto, flags=re.IGNORECASE)
    # Remplazar "Que"/"qué"/"Qué" por "q" (inicio de pregunta o frase)
    texto = re.sub(r'\b[Qq]ue\b', 'q', texto)
    return texto

def limitar_palabras(texto, max_palabras=12):
    palabras = texto.split()
    if len(palabras) > max_palabras:
        return ' '.join(palabras[:max_palabras])
    return texto

def forzar_minuscula(texto):
    texto = texto.strip()
    if texto:
        return texto[0].lower() + texto[1:]
    else:
        return texto

@app.route("/")
def home():
    return "API de autorespuesta activa"

@app.route("/respuesta", methods=["POST"])
def responder():
    data = request.get_json()
    mensaje_usuario = ""
    hora_usuario = ""
    if data and "query" in data:
        if "message" in data["query"]:
            mensaje_usuario = data["query"]["message"]
        if "hora" in data["query"]:
            hora_usuario = data["query"]["hora"]

    if es_respuesta_cerrada(mensaje_usuario):
        return jsonify({"replies": []})

    prompt = PROMPT_LARGO
    if necesita_respuesta_horaria(mensaje_usuario) and hora_usuario:
        ejemplos = buscar_actividad_por_hora(hora_usuario)
        ejemplo = random.choice(ejemplos)
        prompt += f"""\n
IMPORTANTE: El usuario te pregunta "{mensaje_usuario}" a las {hora_usuario}. Responde en menos de 12 palabras, usando el estilo/mala ortografia, guiandote/en el ejemplo: {ejemplo}
No expliques, solo responde directo como si chatearas.
        """

    try:
        completion = openai.chat.completions.create(
             model="gpt-3.5-turbo",  # O "gpt-4-turbo" o "gpt-4o"
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensaje_usuario}
            ],
            max_tokens=70,
            temperature=0.8
        )
        texto_respuesta = completion.choices[0].message.content.strip()
        texto_respuesta = hacer_mala_ortografia(texto_respuesta)
        texto_respuesta = limitar_palabras(texto_respuesta, 25)
        texto_respuesta = forzar_minuscula(texto_respuesta)
    except Exception as e:
        texto_respuesta = f"Error consultando OpenAI: {str(e)}"
    return jsonify({"replies": [{"message": texto_respuesta}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
