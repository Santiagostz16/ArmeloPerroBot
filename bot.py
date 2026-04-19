
#bot.py - Lógica central del bot de Armelo Perro

from gpt_client import GPTClient
from order import Order
from config import Config


class ConversationSession:
    #Representa la sesión de conversación de un cliente.

    def __init__(self, cliente_id: str):
        self.cliente_id: str = cliente_id
        self.history: list[dict] = []
        self.order: Order = Order(cliente_id)

    def add_user_message(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})
        self._trim_history()

    def add_assistant_message(self, message: str) -> None:
        self.history.append({"role": "assistant", "content": message})
        self._trim_history()

    def _trim_history(self) -> None:
        """Mantiene el historial dentro del límite configurado."""
        max_msgs = Config.MAX_HISTORY_MESSAGES
        if len(self.history) > max_msgs:
            self.history = self.history[-max_msgs:]

    def clear(self) -> None:
        """Reinicia la sesión manteniendo el cliente_id."""
        self.history = []
        self.order = Order(self.cliente_id)

    def __repr__(self) -> str:
        return f"<Session cliente={self.cliente_id} msgs={len(self.history)}>"


class ArmeloPetBot:
    #    Bot principal de Armelo Perro.
    # Gestiona múltiples sesiones de clientes y coordina con GPTClient.
    
    def __init__(self):
        self._gpt: GPTClient = GPTClient()
        self._sessions: dict[str, ConversationSession] = {}
        print("[ArmeloPerroBot] Bot inicializado correctamente ✅")

    def _get_or_create_session(self, cliente_id: str) -> ConversationSession:
        #Obtiene la sesión existente del cliente o crea una nueva.
        if cliente_id not in self._sessions:
            self._sessions[cliente_id] = ConversationSession(cliente_id)
            print(f"[ArmeloPerroBot] Nueva sesión creada para: {cliente_id}")
        return self._sessions[cliente_id]

    def process_message(self, cliente_id: str, message: str) -> str:
        """
        Procesa el mensaje de un cliente y retorna la respuesta del bot.

        Args:
            cliente_id: Identificador único del cliente (número de WhatsApp).
            message: Texto del mensaje enviado por el cliente.

        Returns:
            Respuesta en texto del bot.
        """
        session = self._get_or_create_session(cliente_id)

        # Comandos especiales
        if message.strip().lower() in ("/reset", "reiniciar", "nuevo pedido"):
            session.clear()
            return (
                "¡Hola de nuevo, veci! 👋"
                "¿Qué te gustaría pedir hoy en *Armelo Perro*? 🍔🌭"
            )

        # Agregar mensaje del usuario al historial
        session.add_user_message(message)

        # Obtener respuesta de GPT
        response = self._gpt.get_response(session.history)

        # Guardar respuesta en el historial
        session.add_assistant_message(response)

        print(f"[ArmeloPerroBot] [{cliente_id}] Usuario: {message[:60]}...")
        print(f"[ArmeloPerroBot] [{cliente_id}] Bot: {response[:60]}...")

        return response

    def get_session(self, cliente_id: str) -> ConversationSession | None:
        #Retorna la sesión del cliente si existe.
        return self._sessions.get(cliente_id)

    def active_sessions(self) -> int:
        #Retorna el número de sesiones activas.
        return len(self._sessions)

    def remove_session(self, cliente_id: str) -> None:
        #Elimina la sesión de un cliente.
        if cliente_id in self._sessions:
            del self._sessions[cliente_id]
            print(f"[ArmeloPerroBot] Sesión eliminada para: {cliente_id}")