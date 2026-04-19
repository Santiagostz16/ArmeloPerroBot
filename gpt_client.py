"""
gpt_client.py - Cliente LLM para el bot Armelo Perro
=====================================================
Implementa Fine-Tuning via In-Context Learning (ICL).

Al inicializarse, carga el dataset de entrenamiento (training_data.jsonl)
generado por fine_tune.py y selecciona ejemplos representativos para
construir un system prompt enriquecido con few-shot examples.

Este proceso adapta el comportamiento del modelo LLaMA 3.3 70B (Groq)
al dominio específico de Armelo Perro sin requerir modificación de pesos.
"""
import json
import random
import os
from pathlib import Path
from groq import Groq
from config import Config
from menu import Menu


DATASET_PATH = os.path.join(Config.BASE_DIR, "training_data.jsonl")
N_FEW_SHOT_EXAMPLES = 15  # ejemplos del dataset a incluir en cada sesión


def _load_dataset() -> list[dict]:
    """Carga el dataset JSONL generado por fine_tune.py."""
    if not Path(DATASET_PATH).exists():
        return []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _build_system_prompt(menu_texto: str, examples: list[dict]) -> str:
    """
    Construye el system prompt con few-shot examples del dataset.
    Soporta datasets en formato:
    - {"input": "...", "output": "..."}
    - {"prompt": "...", "completion": "..."}
    """

    few_shot_block = ""

    if examples:
        selected = random.sample(examples, min(N_FEW_SHOT_EXAMPLES, len(examples)))
        lines = ["\n## EJEMPLOS DE ENTRENAMIENTO (Few-Shot Learning):"]

        for i, ex in enumerate(selected, 1):
            lines.append(f"\nEjemplo {i}:")

            try:
                # Caso 1: formato input/output
                if "input" in ex and "output" in ex:
                    user = ex["input"]
                    bot = ex["output"]

                # Caso 2: formato prompt/completion (tu caso)
                elif "prompt" in ex and "completion" in ex:
                    prompt = ex.get("prompt", "")
                    completion = ex.get("completion", "")

                    if "Cliente:" in prompt:
                        user = prompt.split("Cliente:")[1].split("\n")[0].strip()
                    else:
                        user = prompt.strip()

                    bot = completion.strip()

                # Caso desconocido
                else:
                    user = str(ex)
                    bot = "Formato no reconocido"

            except Exception as e:
                print("[GPTClient] Error procesando ejemplo:", ex)
                user = "???"
                bot = "???"

            lines.append(f"  Cliente: {user}")
            lines.append(f"  Perrito: {bot}")

        few_shot_block = "\n".join(lines)
        source = f"dataset ({len(examples)} ejemplos supervisados)"

    else:
        source = "instrucciones base (ejecuta fine_tune.py --generate para activar few-shot)"

    print(f"[GPTClient] Fine-tuning activo via: {source}")

    return f"""Eres *Perrito*, el asistente virtual oficial de *Armelo Perro* 🌭🍔, un restaurante de fast food colombiano.
Tu rol es atender a los clientes de manera amigable, cálida y eficiente, exclusivamente en español.

---
{menu_texto}

---

## TUS RESPONSABILIDADES:

1. Saludar al cliente brevemente cuando inicie la conversación.
    - No uses saludos genéricos como "Hola, ¿en qué puedo ayudarte?" o "Bienvenido". Sé más cercano y cálido, por ejemplo: "¡Hola veci! ¿Qué se te antoja hoy? 🌭🍔".
    - No uses el emoji de Perro, el cliente no sabe que eres un bot. Usa emojis de comida o saludos.
2. Tomar el pedido: responde dudas sobre productos, precios y combos.
3. Preguntar la modalidad: come en el restaurante, para llevar o domicilio?
   - Si es domicilio: pedir dirección de entrega.
4. Preguntar los toppings y salsas solo si es domicilio (en restaurante el cliente los pone en la barra).
5. Confirmar el pedido con un resumen corto antes de finalizar.
6. Informar el total incluyendo empaque si aplica.
7. Preguntar el método de pago: Efectivo, Tarjeta, Nequi, Daviplata o Bold.
8. Despedirse brevemente una vez confirmado el pedido.

## REGLAS IMPORTANTES:

- Habla en español colombiano cercano y cálido. Expresiones como "listo", "claro que sí", "con mucho gusto", expresate a los clientes como "veci" son bienvenidas.
- EXPRESIONES COLOMBIANAS: Cuando el cliente diga "me regalas" o "regálame", entiende que significa "quiero comprar" o "me vendes". Es una expresión local, NO significa que te lo pidan gratis. Responde normalmente tomando el pedido. No digas que no le puedes regalar el producto.
- Nunca inventes precios ni productos que no estén en el menú.
- Para Hamburguesa Orellana y Hamburguesa Bestial: el precio debe consultarse en el restaurante.
- La barra de toppings es gratis e ilimitada en restaurante y para llevar (el cliente los pone él mismo).
- Para domicilio, el cliente indica sus toppings y salsas al pedir.
- Una vez el cliente prueba el producto en el restaurante, NO se pueden agregar más toppings.
- Empaque: $500 para 1 producto, $1.000 para más de uno (solo llevar/domicilio).
- Si no sabes algo, remite al equipo del restaurante.
- No respondas temas ajenos al restaurante.

## ESTILO DE RESPUESTA - MUY IMPORTANTE:
- Se BREVE y DIRECTO. Máximo 3-4 líneas por mensaje.
- No expliques de más. Una pregunta = una respuesta corta.
- Usa emojis con moderación (1-2 por mensaje máximo).

## FLUJO:
Saludo corto → Pedido → Modalidad → Toppings (solo domicilio) → Resumen → Pago → Despedida
"""



class GPTClient:
    
    """Cliente LLM que implementa Fine-Tuning via In-Context Learning.

    Carga el dataset supervisado generado por fine_tune.py e inyecta
    ejemplos representativos en cada system prompt para adaptar el
    comportamiento del modelo al dominio de Armelo Perro.

    Técnica: Few-Shot Prompt Tuning sobre LLaMA 3.3 70B via Groq API.
    """

    def __init__(self):
        self._client = Groq(api_key=Config.GROQ_API_KEY)
        self._menu = Menu()

        # Cargar dataset de entrenamiento (generado por fine_tune.py)
        self._dataset = _load_dataset()

        # Construir system prompt enriquecido con few-shot examples
        self._system_prompt = _build_system_prompt(
            self._menu.to_prompt_text(),
            self._dataset,
        )
        print(f"[GPTClient] Groq inicializado | Modelo: {Config.GROQ_MODEL} ✅")

    def get_response(self, conversation_history: list[dict]) -> str:
        """
        Genera una respuesta usando el modelo fine-tuneado via ICL.

        Args:
            conversation_history: Lista [{"role": "user/assistant", "content": "..."}]

        Returns:
            Respuesta del asistente como string.
        """
        messages = [{"role": "system", "content": self._system_prompt}]
        messages.extend(conversation_history[-Config.MAX_HISTORY_MESSAGES:])

        try:
            response = self._client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=messages,
                max_tokens=Config.OPENAI_MAX_TOKENS,
                temperature=Config.OPENAI_TEMPERATURE,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[GPTClient] Error al generar respuesta: {e}")
            return (
                "Lo siento, tuve un problema técnico 😅. "
                "Por favor intenta de nuevo en un momento."
            )

    @property
    def dataset_size(self) -> int:
        """Retorna el número de ejemplos de entrenamiento cargados."""
        return len(self._dataset)
