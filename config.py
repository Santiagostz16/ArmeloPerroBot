"""
config.py - Configuración y variables de entorno del bot Armelo Perro
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Clase de configuración central del proyecto."""

    # Groq (GRATIS y ultra rápido)
    # Obtén tu API key gratis en: https://console.groq.com
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Parámetros de generación
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "800"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv(
        "TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"
    )

    # Flask
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Rutas
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    MENU_DATA_PATH: str = os.path.join(BASE_DIR, "menu_data.json")

    # Conversación
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

    @classmethod
    def validate(cls) -> None:
        """Valida que las variables críticas estén configuradas."""
        missing = []
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not cls.TWILIO_ACCOUNT_SID:
            missing.append("TWILIO_ACCOUNT_SID")
        if not cls.TWILIO_AUTH_TOKEN:
            missing.append("TWILIO_AUTH_TOKEN")
        if missing:
            raise EnvironmentError(
                f"Faltan las siguientes variables de entorno: {', '.join(missing)}\n"
                f"Por favor configura el archivo .env"
            )
