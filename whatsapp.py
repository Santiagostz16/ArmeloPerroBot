#whatsapp.py - Manejador de mensajes de WhatsApp via Twilio
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config import Config


class WhatsAppHandler:
    
    #Maneja el envío y recepción de mensajes de WhatsApp usando Twilio.
    

    def __init__(self):
        self._client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self._from_number = Config.TWILIO_WHATSAPP_NUMBER
        print("[WhatsAppHandler] Twilio inicializado ✅")

    def parse_incoming(self, form_data: dict) -> tuple[str, str]:
        """
        Extrae el número del cliente y el mensaje del webhook de Twilio.

        Args:
            form_data: Datos del formulario del webhook (request.form).

        Returns:
            Tupla (cliente_id, message_text)
        """
        sender = form_data.get("From", "")  
        message = form_data.get("Body", "").strip()
        return sender, message

    def build_twiml_response(self, reply_text: str) -> str:
        """
        Construye la respuesta TwiML para enviar al webhook de Twilio.

        Args:
            reply_text: Texto de la respuesta del bot.

        Returns:
            String XML de respuesta TwiML.
        """
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(reply_text)
        return str(resp)

    def send_message(self, to: str, body: str) -> None:
        """
        Envía un mensaje activo (fuera del flujo de webhook) a un cliente.

        Args:
            to: Número destino en formato "whatsapp:+573001234567".
            body: Texto del mensaje a enviar.
        """
        try:
            message = self._client.messages.create(
                from_=self._from_number,
                to=to,
                body=body,
            )
            print(f"[WhatsAppHandler] Mensaje enviado a {to} | SID: {message.sid}")
        except Exception as e:
            print(f"[WhatsAppHandler] Error enviando mensaje a {to}: {e}")
