#main.py - Servidor Flask principal del bot de WhatsApp de Armelo Perro
from flask import Flask, request, Response
from config import Config
from bot import ArmeloPetBot
from whatsapp import WhatsAppHandler

# Inicialización 
Config.validate()

app = Flask(__name__)
bot = ArmeloPetBot()
whatsapp = WhatsAppHandler()


# Rutas 
@app.route("/webhook", methods=["POST"])
def webhook():
    
    #Endpoint principal del webhook de Twilio.
    #Recibe mensajes de WhatsApp, los procesa con el bot y responde.
    
    # 1. Parsear mensaje entrante
    cliente_id, mensaje = whatsapp.parse_incoming(request.form)

    if not mensaje:
        return Response(str(""), mimetype="text/xml")

    print(f"\n[Webhook] Mensaje de {cliente_id}: {mensaje}")

    # 2. Procesar con el bot
    respuesta = bot.process_message(cliente_id, mensaje)

    # 3. Construir y retornar TwiML
    twiml = whatsapp.build_twiml_response(respuesta)
    return Response(twiml, mimetype="text/xml")


@app.route("/status", methods=["GET"])
def status():
    #Endpoint de estado para verificar que el servidor está activo.
    return {
        "status": "online",
        "bot": "Armelo Perro Bot 🌭",
        "sesiones_activas": bot.active_sessions(),
        "modelo": Config.GROQ_MODEL,
    }


@app.route("/", methods=["GET"])
def home():
    #Ruta raíz con información básica.
    return (
        "<h1>🌭 Armelo Perro Bot</h1>"
        "<p>El bot de WhatsApp de Armelo Perro está corriendo.</p>"
        "<p>Webhook: <code>POST /webhook</code></p>"
        "<p>Estado: <a href='/status'>/status</a></p>"
    )


# Entry point

if __name__ == "__main__":
    print("=" * 50)
    print("🌭 Armelo Perro Bot - Iniciando servidor...")
    print(f"   Host    : {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"   Modelo  : {Config.GROQ_MODEL}")
    print(f"   Webhook : http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/webhook")
    print("=" * 50)
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )
