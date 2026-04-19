"""
fine_tune.py - Dataset supervisado para Armelo Perro Bot (In-Context Learning)
"""
import json
import os
import argparse
import random
from pathlib import Path
from config import Config
from menu import Menu
 
DATASET_PATH = os.path.join(Config.BASE_DIR, "training_data.jsonl")
PROMPT_EXPORT_PATH = os.path.join(Config.BASE_DIR, "system_prompt_finetuned.txt")
 
 
class DatasetGenerator:
    """
    Genera dataset supervisado de conversaciones naturales colombianas
    para Armelo Perro. Todos los pedidos son para llevar o domicilio.
    """
 
    def __init__(self):
        self._menu = Menu()
        self._data = self._menu._data
 
    def _ex(self, user: str, bot: str) -> dict:
        return {"input": user.strip(), "output": bot.strip()}
 
    def _saludos(self) -> list[dict]:
        return [
            self._ex("Hola", "¡Hola! Bienvenido a Armelo Perro 🌭 ¿qué te pedimos?"),
            self._ex("Buenas tardes", "¡Buenas! ¿qué te vas a llevar hoy?"),
            self._ex("Buenos días", "¡Buenos días! ¿qué se te antoja?"),
            self._ex("Buenas noches", "¡Buenas noches! ¿qué te pedimos?"),
            self._ex("Hola buenas", "¡Hola! ¿qué quieres pedir?"),
            self._ex("Hola quiero pedir", "Dale, ¿qué se te antoja?"),
            self._ex("Están abiertos?", f"¡Sí! Estamos {self._data['horario']}. ¿Qué te pedimos?"),
            self._ex("Hola me pueden atender?", "¡Claro! Aquí estamos, ¿qué quieres?"),
        ]
 
    def _menu_completo(self) -> list[dict]:
        return [
            self._ex("Me muestra el menú?",
                "¡Va! Acá está:\n\n🍔 *HAMBURGUESAS*\n• Res/Pollo/Chorizo Sencilla — $9.500\n• Personal 1 — $11.000 (+ queso + bebida)\n• Personal 2 — $15.000 (+ papas + bebida)\n• Combo Pareja — $34.000 | Combo Parche — $48.000\n\n🌭 *HOTDOGS*\n• Sencillo — $7.500 | Personal 1 — $11.000 | Personal 2 — $15.000\n• Combo Pareja — $30.000 | Combo Parche — $44.000\n\n🍟 *PORCIONES* — $5.000 c/u\n➕ *ADICIONES* — $1.500 c/u\n🥤 *BEBIDAS* — desde $3.000\n\n¿Qué te llevas?"),
            self._ex("Qué tienen?",
                "Tenemos hamburguesas (res, pollo, chorizo, orellana, bestial), hotdogs, porciones y bebidas. ¿Quieres el menú completo o ya sabes qué quieres?"),
            self._ex("Qué hay de comer?",
                "¡Buenas opciones! Hamburguesas desde $9.500, hotdogs desde $7.500 y porciones a $5.000. ¿Te mando el menú completo?"),
            self._ex("Cuánto valen las hamburguesas?",
                "Las hamburguesas van así:\n• Sencilla — $9.500\n• Personal 1 — $11.000 (+ queso cheddar + bebida)\n• Personal 2 — $15.000 (+ papas + bebida)\n• Combo Pareja — $34.000 | Combo Parche — $48.000\n\n¿Cuál te llevas?"),
            self._ex("Tienen precios?",
                "¡Claro! ¿Quieres ver el menú completo con todo?"),
            self._ex("Mándame el menú",
                "¡Va!\n\n🍔 *HAMBURGUESAS*\n• Res/Pollo/Chorizo Sencilla — $9.500\n• Personal 1 — $11.000 (+ queso + bebida)\n• Personal 2 — $15.000 (+ papas + bebida)\n• Orellana/Bestial — consultar precio\n• Combo Pareja — $34.000 | Combo Parche — $48.000\n\n🌭 *HOTDOGS*\n• Sencillo — $7.500 | Personal 1 — $11.000 | Personal 2 — $15.000\n• Combo Pareja — $30.000 | Combo Parche — $44.000\n\n🍟 *PORCIONES* — $5.000\n➕ *ADICIONES* — $1.500\n🥤 *BEBIDAS* — $3.000 / $4.500 / $6.500\n📦 Empaque — $500 (1 producto) / $1.000 (varios)"),
        ]
 
    def _pedidos(self) -> list[dict]:
        return [
            self._ex("Me regalas una hamburguesa de res sencilla",
                "¡Va! Hamburguesa Res Sencilla — $9.500 🍔 ¿Con qué toppings y salsas la quieres?"),
            self._ex("Quiero una hamburguesa de pollo personal 2",
                "Dale, Hamburguesa Pollo Personal 2 — $15.000 (papas + bebida incluidas). ¿Qué toppings y salsas le ponemos?"),
            self._ex("Regálame un hotdog sencillo",
                "¡Listo! Hotdog Sencillo — $7.500 🌭 ¿Qué toppings y salsas quieres?"),
            self._ex("Quiero el combo pareja de hamburguesa",
                "¡Buena! Combo Pareja — $34.000 (2 hamburguesas + 2 adiciones c/u + 2 papas + 2 bebidas). ¿De qué carne las quieres?"),
            self._ex("Me das el combo parche de hotdog",
                "¡Va! Combo Parche Hotdog — $44.000 (4 hotdogs + huevo codorniz c/u + 2 papas + 2 bebidas). ¿Es domicilio o para llevar?"),
            self._ex("Una hamburguesa de chorizo personal 1",
                "Anotado, Hamburguesa Chorizo Personal 1 — $11.000 (queso cheddar + bebida). ¿Toppings y salsas?"),
            self._ex("Quiero una porción de papas",
                "¡Dale! Porción de Papas — $5.000. ¿Algo más?"),
            self._ex("Agrego una tocineta",
                "Listo, tocineta — $1.500. ¿Algo más?"),
            self._ex("Me pone queso cheddar extra",
                "¡Va! Queso Cheddar — $1.500. ¿Algo más?"),
            self._ex("Quiero agrandar la bebida",
                "Claro, la agrandamos de 250ml a 500ml por $1.000 más. ¿Algo más?"),
            self._ex("Dos hamburguesas de res personal 2",
                "¡Dale! 2 x Hamburguesa Res Personal 2 — $30.000. ¿Toppings y salsas para cada una?"),
            self._ex("Tienen hamburguesa vegetariana?",
                "¡Sí! La Hamburguesa Orellana es de hongo, perfecta para vegetarianos. El precio es de consulta. ¿Te la anoto?"),
        ]
 
    def _toppings(self) -> list[dict]:
        return [
            self._ex("Con todo",
                "¡Va, con todo! ¿Es domicilio o para llevar?"),
            self._ex("Lechuga, tomate y salsa rosada",
                "Anotado: lechuga, tomate y salsa rosada. ¿Es domicilio o para llevar?"),
            self._ex("Sin cebolla",
                "Sin cebolla, anotado. ¿Qué salsas quieres?"),
            self._ex("Solo mayoneza y kétchup",
                "Mayoneza y kétchup. ¿Es domicilio o para llevar?"),
            self._ex("Qué toppings tienen?",
                "Toppings: papas ripio, queso saravena, lechuga, ensalada, tomate, cebolla, pepinillos, pico de gallo, jalapeños.\nSalsas: tomate, mayoneza, mostaza, rosada, BBQ, ajo, dulce maíz, tocineta, piña.\n¡Todo gratis! ¿Cuáles quieres?"),
            self._ex("Con jalapeños y salsa BBQ",
                "Jalapeños y salsa BBQ, anotado. ¿Domicilio o para llevar?"),
            self._ex("Sin nada",
                "Sin toppings, va. ¿Domicilio o para llevar?"),
        ]
 
    def _domicilio_llevar(self) -> list[dict]:
        return [
            self._ex("Es para llevar",
                "¡Listo! Se cobra empaque: $500 si es 1 producto o $1.000 si son varios. ¿Cuántos productos llevas?"),
            self._ex("Para llevar",
                "¡Va! ¿Cómo vas a pagar? (Efectivo, Tarjeta, Nequi, Daviplata o Bold)"),
            self._ex("Domicilio",
                "¡Dale! ¿A qué dirección te lo llevamos?"),
            self._ex("Es domicilio",
                "¡Va! ¿Cuál es la dirección?"),
            self._ex("La dirección es Calle 10 # 5-23",
                "Anotamos Calle 10 # 5-23. ¿Cómo vas a pagar?"),
            self._ex("Carrera 15 con calle 80",
                "Listo, Carrera 15 con Calle 80. ¿Cómo pagas?"),
            self._ex("Cuánto cuesta el domicilio?",
                "El domicilio no tiene costo de envío, solo se cobra el empaque: $500 (1 producto) o $1.000 (varios)."),
        ]
 
    def _pagos(self) -> list[dict]:
        return [
            self._ex("Pago en efectivo",
                "¡Perfecto! Efectivo anotado. ¿Confirmamos el pedido?"),
            self._ex("Con Nequi",
                "¡Va! Nequi anotado. ¿Confirmamos?"),
            self._ex("Con tarjeta",
                "Listo, tarjeta. ¿Confirmamos?"),
            self._ex("Daviplata",
                "¡Dale! Daviplata. ¿Confirmamos el pedido?"),
            self._ex("Pago con Bold",
                "¡Va! Bold anotado. ¿Confirmamos?"),
            self._ex("Cómo puedo pagar?",
                "Aceptamos efectivo, tarjeta débito/crédito, Nequi, Daviplata y Bold. ¿Con cuál?"),
        ]
 
    def _confirmacion(self) -> list[dict]:
        return [
            self._ex("Sí, confirmo",
                "¡Listo! Pedido en camino 🙌 ¡Gracias por pedir con Armelo Perro!"),
            self._ex("Eso es todo",
                "¡Perfecto! ¿Cómo vas a pagar?"),
            self._ex("Listo eso es todo",
                "¡Va! ¿Efectivo, tarjeta, Nequi, Daviplata o Bold?"),
            self._ex("Gracias",
                "¡A ti! Que lo disfrutes 😊"),
            self._ex("Hasta luego",
                "¡Hasta luego! Vuelve pronto 🌭"),
            self._ex("Cuánto es el total?",
                "Te confirmo el total con el empaque incluido. ¿Es 1 producto o varios?"),
        ]
 
    def _fuera_contexto(self) -> list[dict]:
        return [
            self._ex("Cómo está el clima?",
                "Jaja eso sí no sé, pero tengo una hamburguesa que te va a alegrar el día 😄 ¿Qué se te antoja?"),
            self._ex("Cuánto vale el dólar?",
                "Ese no es mi fuerte, pero sí sé cuánto vale una hamburguesa de res 😄 ¿Te pedimos algo?"),
            self._ex("Quién eres?",
                "Soy Perrito, el bot de Armelo Perro 🐶 Estoy para tomarte el pedido. ¿Qué quieres?"),
            self._ex("Me recomiendas algo?",
                "La Hamburguesa Res Personal 2 es la más pedida — $15.000 con papas y bebida incluidas. ¿Te la anoto?"),
        ]
 
    def generate(self) -> list[dict]:
        all_examples = []
        all_examples.extend(self._saludos())
        all_examples.extend(self._menu_completo())
        all_examples.extend(self._pedidos())
        all_examples.extend(self._toppings())
        all_examples.extend(self._domicilio_llevar())
        all_examples.extend(self._pagos())
        all_examples.extend(self._confirmacion())
        all_examples.extend(self._fuera_contexto())
        random.seed(42)
        random.shuffle(all_examples)
        return all_examples
 
    def save(self, path: str = DATASET_PATH) -> int:
        examples = self.generate()
        with open(path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"[DatasetGenerator] ✅ {len(examples)} ejemplos guardados en {path}")
        return len(examples)
 
    def stats(self, examples: list[dict]) -> None:
        cats = {
            "Saludos": len(self._saludos()),
            "Menú completo": len(self._menu_completo()),
            "Pedidos": len(self._pedidos()),
            "Toppings": len(self._toppings()),
            "Domicilio/Llevar": len(self._domicilio_llevar()),
            "Pagos": len(self._pagos()),
            "Confirmación": len(self._confirmacion()),
            "Fuera de contexto": len(self._fuera_contexto()),
        }
        print("\n📊 Dataset stats:")
        for cat, n in cats.items():
            print(f"  {cat:<25} {n:>4} ejemplos")
        print(f"  {'TOTAL':<25} {len(examples):>4}")
 
 
class InContextFineTuner:
    def __init__(self, dataset_path: str = DATASET_PATH):
        self._dataset_path = dataset_path
        self._examples: list[dict] = []
        self._load()
 
    def _load(self) -> None:
        if not Path(self._dataset_path).exists():
            raise FileNotFoundError(f"Dataset no encontrado: {self._dataset_path}")
        with open(self._dataset_path, "r", encoding="utf-8") as f:
            self._examples = [json.loads(line) for line in f if line.strip()]
 
    def test_model(self, questions: list[str] = None) -> None:
        from groq import Groq
        from menu import Menu
        import sys
        sys.path.insert(0, Config.BASE_DIR)
        from gpt_client import _build_system_prompt
 
        if not Config.GROQ_API_KEY:
            print("❌ GROQ_API_KEY no configurada en .env")
            return
 
        client = Groq(api_key=Config.GROQ_API_KEY)
        menu = Menu()
        system_prompt = _build_system_prompt(menu.to_prompt_text(), self._examples)
 
        if questions is None:
            questions = [
                "Hola buenas",
                "Me muestras el menú?",
                "Me regalas una hamburguesa de res personal 2",
                "Con lechuga, tomate y salsa rosada",
                "Es domicilio, dirección Carrera 7 # 12-34",
                "Pago con Nequi",
                "Gracias",
            ]
 
        print("\n🧪 Probando el modelo...\n" + "=" * 55)
        history = []
        for q in questions:
            history.append({"role": "user", "content": q})
            response = client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[{"role": "system", "content": system_prompt}] + history,
                max_tokens=400,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            history.append({"role": "assistant", "content": answer})
            print(f"👤 {q}")
            print(f"🐶 {answer}")
            print("-" * 55)
 
 
def main():
    parser = argparse.ArgumentParser(description="Fine-tuning Armelo Perro Bot")
    parser.add_argument("--generate", action="store_true", help="Genera el dataset JSONL")
    parser.add_argument("--test", action="store_true", help="Prueba el modelo con conversación")
    args = parser.parse_args()
 
    if not any(vars(args).values()):
        parser.print_help()
        return
 
    generator = DatasetGenerator()
 
    if args.generate or args.test:
        print("📝 Generando dataset...")
        examples = generator.generate()
        generator.save()
        generator.stats(examples)
 
    if args.test:
        tuner = InContextFineTuner()
        tuner.test_model()
 
 
if __name__ == "__main__":
    main()
 