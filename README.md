# 🌭 Armelo Perro Bot — WhatsApp Chatbot

Bot de WhatsApp impulsado por GPT para el restaurante de fast food **Armelo Perro**.
Atiende clientes en español, toma pedidos, informa el menú y gestiona domicilios.

---

## 📁 Estructura del Proyecto

```
armelo_perro_bot/
├── main.py           # Servidor Flask + webhook de Twilio
├── bot.py            # Lógica central del bot (OOP)
├── gpt_client.py     # Cliente OpenAI GPT con system prompt
├── whatsapp.py       # Manejador Twilio WhatsApp
├── menu.py           # Cargador y representación del menú
├── order.py          # Clases de gestión de pedidos
├── config.py         # Configuración centralizada
├── menu_data.json    # Datos del menú en JSON
├── requirements.txt  # Dependencias Python
├── .env.example      # Plantilla de variables de entorno
└── README.md         # Este archivo
```

---

## ⚙️ Instalación

### 1. Clonar o descargar el proyecto

```bash
cd armelo_perro_bot
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus claves reales:

| Variable | Descripción | Dónde obtenerla |
|---|---|---|
| `OPENAI_API_KEY` | Clave de la API de OpenAI | [platform.openai.com](https://platform.openai.com) |
| `TWILIO_ACCOUNT_SID` | SID de tu cuenta Twilio | [console.twilio.com](https://console.twilio.com) |
| `TWILIO_AUTH_TOKEN` | Token de autenticación Twilio | [console.twilio.com](https://console.twilio.com) |
| `TWILIO_WHATSAPP_NUMBER` | Número Twilio (sandbox: `whatsapp:+14155238886`) | Twilio Sandbox |

---

## 🚀 Correr el servidor

```bash
python main.py
```

El servidor corre en `http://localhost:5000`.

---

## 📱 Configurar Twilio WhatsApp Sandbox

### Paso 1 — Activar el Sandbox

1. Ve a [console.twilio.com](https://console.twilio.com)
2. Navega a **Messaging → Try it out → Send a WhatsApp message**
3. Envía el código de activación al número sandbox desde tu WhatsApp personal (ej: `join [palabra]`)

### Paso 2 — Exponer tu servidor local con ngrok

Twilio necesita una URL pública para enviar los mensajes. Usa **ngrok**:

```bash
# Instalar ngrok: https://ngrok.com/download
ngrok http 5000
```

Copia la URL HTTPS que te da ngrok, por ejemplo:
```
https://abc123.ngrok.io
```

### Paso 3 — Configurar el Webhook en Twilio

1. En la consola de Twilio, ve a tu Sandbox de WhatsApp
2. En el campo **"When a message comes in"**, pega:
   ```
   https://abc123.ngrok.io/webhook
   ```
3. Método: **HTTP POST**
4. Guarda los cambios

### Paso 4 — ¡Probar!

Envía un mensaje desde tu WhatsApp al número sandbox de Twilio. El bot responderá automáticamente.

---

## 💬 Funcionalidades del Bot

| Función | Descripción |
|---|---|
| 🍔 Menú completo | Conoce todos los productos, combos y precios |
| 📋 Tomar pedidos | Guía al cliente paso a paso |
| 🧄 Toppings y salsas | Gestiona la barra de ingredientes |
| 🛵 Modalidades | Restaurante, para llevar o domicilio |
| 💳 Pagos | Informa métodos: efectivo, tarjeta, Nequi, Daviplata, Bold |
| 🔄 Reiniciar | El cliente puede escribir `reiniciar` para empezar de nuevo |

---

## 🏗️ Arquitectura OOP

```
ArmeloPetBot          ← Orquestador principal
├── GPTClient         ← Comunicación con OpenAI
├── WhatsAppHandler   ← Integración Twilio
├── ConversationSession[] ← Historial por cliente
│   └── Order         ← Pedido actual del cliente
│       └── ItemPedido[]
└── Menu              ← Datos del menú
    └── MenuItem[]
```

---

## 🔧 Comandos especiales del cliente

| Comando | Acción |
|---|---|
| `reiniciar` | Reinicia la conversación y el pedido |
| `nuevo pedido` | Igual que reiniciar |
| `/reset` | Igual que reiniciar |

---

## 📌 Notas importantes

- **Hamburguesa Orellana** y **Hamburguesa Bestial** no tienen precio definido; el bot indicará que debe consultarse.
- La barra de toppings es **gratuita e ilimitada** para consumo en el restaurante y para llevar.
- Para **domicilios**, el cliente especifica sus toppings en el chat.
- **Una vez el cliente prueba el producto en el restaurante**, no se pueden agregar más toppings.

---

## 🛠️ Tecnologías usadas

- **Python 3.11+**
- **OpenAI GPT-4o-mini** — Motor de lenguaje natural
- **Flask** — Servidor web / webhook
- **Twilio** — Integración WhatsApp
- **ngrok** — Túnel para desarrollo local

---

*Proyecto académico — Text Analytics & Intelligent Systems*
