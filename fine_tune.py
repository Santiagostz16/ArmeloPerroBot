"""
fine_tune.py - Generación de dataset y fine-tuning del modelo para Armelo Perro
===============================================================================
Este script realiza DOS cosas:
  1. Genera un dataset de conversaciones (JSONL) basado en el menú real
  2. Fine-tunea un modelo LLM pequeño (TinyLlama / DialoGPT) usando ese dataset

Ejecutar:
    python fine_tune.py --generate   # Solo genera el dataset
    python fine_tune.py --train      # Genera dataset y entrena el modelo
    python fine_tune.py --both       # Ambos pasos (recomendado primera vez)

El modelo entrenado se guarda en ./finetuned_model/ 
"""

import json
import os
import argparse
import random
from pathlib import Path
from config import Config
from menu import Menu


# Rutas
DATASET_PATH = os.path.join(Config.BASE_DIR, "training_data.jsonl")
MODEL_OUTPUT_PATH = os.path.join(Config.BASE_DIR, "finetuned_model")
BASE_MODEL = "microsoft/DialoGPT-small" 

# GENERADOR DE DATASET
class DatasetGenerator:
    
    #Genera un dataset de conversaciones de cliente-bot para Armelo Perro.
    #Cada ejemplo sigue el formato de fine-tuning: prompt → completion.
    def __init__(self):
        self._menu = Menu()
        self._data = self._menu._data
        self._examples: list[dict] = []

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _example(self, user: str, bot: str) -> dict:
        #Crea un ejemplo de entrenamiento en formato prompt/completion.
        return {
            "prompt": f"Cliente: {user}\nPerrito:",
            "completion": f" {bot.strip()}"
        }

    def _price(self, p: int | None) -> str:
        if p is None:
            return "consultar precio"
        return f"${p:,.0f}".replace(",", ".")

    # Categorías 
    def _gen_saludos(self) -> list[dict]:
        saludos = [
            ("Hola", "¡Hola! Bienvenido a *Armelo Perro* 🌭 ¿Qué te provoca hoy?"),
            ("Buenas tardes", "¡Buenas tardes! Bienvenido a *Armelo Perro*. ¿Qué te pedimos?"),
            ("Hola buenas", "¡Hola! Con mucho gusto. ¿Qué vas a querer hoy?"),
            ("Buenos días", "¡Buenos días! Bienvenido. ¿Qué te provoca de nuestro menú?"),
            ("Buenas noches", "¡Buenas noches! Listo para atenderte. ¿Qué te pedimos?"),
            ("Hola quiero pedir", "¡Claro que sí! ¿Qué te vas a llevar hoy?"),
            ("Me ayudas con un pedido?", "¡Con mucho gusto! ¿Qué te provoca?"),
        ]
        return [self._example(u, b) for u, b in saludos]

    def _gen_preguntas_menu(self) -> list[dict]:
        examples = []
        menu = self._data["menu"]

        # Preguntas generales del menú
        examples.append(self._example(
            "Qué tienen en el menú?",
            "Tenemos hamburguesas (res, pollo, chorizo, orellana, bestial), hotdogs y porciones. "
            "También bebidas y adiciones. ¿Qué se te antoja?"
        ))
        examples.append(self._example(
            "Qué hamburguesas tienen?",
            "Tenemos de *Res*, *Pollo*, *Chorizo*, *Orellana* (hongo) y la *Bestial* (res+chorizo+tocineta). "
            "Cada una tiene opción Sencilla, Personal 1 y Personal 2. ¿Cuál te llama la atención?"
        ))
        examples.append(self._example(
            "Tienen hotdog?",
            "¡Sí! Hotdog con salchicha americana Zenú. Desde $7.500 el sencillo. "
            "También tenemos combos Pareja y Parche. ¿Te interesa?"
        ))
        examples.append(self._example(
            "Cuánto vale la hamburguesa?",
            "La hamburguesa sencilla vale *$9.500*, el Personal 1 *$11.000* y el Personal 2 *$15.000*. ¿Cuál prefieres?"
        ))

        # Preguntas sobre combos específicos
        for h in menu["hamburguesas"]:
            for op in h["opciones"]:
                precio = self._price(op.get("precio"))
                examples.append(self._example(
                    f"Cuánto vale la {h['nombre']} {op['combo']}?",
                    f"La *{h['nombre']} {op['combo']}* vale *{precio}*. Incluye: {op['descripcion']}."
                ))

        for op in menu["hotdogs"][0]["opciones"]:
            precio = self._price(op.get("precio"))
            examples.append(self._example(
                f"Cuánto vale el hotdog {op['combo']}?",
                f"El *Hotdog {op['combo']}* vale *{precio}*. Incluye: {op['descripcion']}."
            ))

        return examples

    def _gen_toppings(self) -> list[dict]:
        toppings = self._data["barra_toppings"]["toppings"]
        salsas = self._data["barra_toppings"]["salsas"]
        examples = [
            self._example(
                "Qué toppings tienen?",
                f"En la barra tienes: {', '.join(toppings)}. ¡Todo gratis y sin límite! 🎉"
            ),
            self._example(
                "Qué salsas tienen?",
                f"Tenemos: {', '.join(salsas)}. Todas gratis en la barra."
            ),
            self._example(
                "La barra es gratis?",
                "¡Sí! La barra de toppings y salsas es completamente gratis. Pon todo lo que quieras 🙌"
            ),
            self._example(
                "Puedo poner más toppings después de probar?",
                "Una vez que le das el primer mordisco al producto, ya no se pueden agregar más toppings. "
                "¡Aprovecha la barra antes de comer!"
            ),
            self._example(
                "Para domicilio puedo escoger toppings?",
                "¡Claro! Para domicilio dinos aquí qué toppings y salsas quieres y nosotros los ponemos antes de empacar."
            ),
        ]
        return examples

    def _gen_pedidos(self) -> list[dict]:
        """Genera ejemplos de flujo completo de pedido."""
        examples = [
            # Expresión colombiana "me regalas"
            self._example(
                "Me regalas una hamburguesa de res sencilla",
                "¡Listo! Una *Hamburguesa Res Sencilla* por *$9.500*. ¿Es para comer aquí, para llevar o domicilio?"
            ),
            self._example(
                "Regálame un hotdog personal 2",
                "¡Con gusto! Un *Hotdog Personal 2* por *$15.000* (salchicha, papas fritas y bebida 250ml). "
                "¿Para comer aquí, llevar o domicilio?"
            ),
            self._example(
                "Quiero una hamburguesa de pollo personal 1",
                "Anotado, *Hamburguesa Pollo Personal 1* — *$11.000* (pollo, queso cheddar y bebida). "
                "¿La comes aquí, la llevas o es domicilio?"
            ),
            self._example(
                "Me das el combo pareja de hamburguesa",
                "¡Perfecto! El *Combo Pareja* cuesta *$34.000* e incluye 2 hamburguesas de la carne que escojas, "
                "2 adiciones c/u, 2 papas y 2 bebidas. ¿Qué carne quieres para cada una?"
            ),
            self._example(
                "Quiero el combo parche de hotdog",
                "¡Buena elección! El *Combo Parche Hotdog* vale *$44.000* — 4 hotdogs con huevo de codorniz, "
                "2 papas fritas y 2 bebidas. ¿Es para comer aquí o llevan?"
            ),
            self._example(
                "Quiero una porción de papas",
                "Claro, una *Porción de Papas Fritas* por *$5.000* (150g). ¿Algo más?"
            ),
            self._example(
                "Me agrego una tocineta",
                "¡Listo! Una *Tocineta* por *$1.500* agregada. ¿Algo más o cerramos el pedido?"
            ),
        ]
        return examples

    def _gen_modalidades(self) -> list[dict]:
        return [
            self._example(
                "Es para llevar",
                "¡Perfecto! Para llevar se cobra un empaque. ¿Es un solo producto o más de uno?"
            ),
            self._example(
                "Para llevar un producto",
                "Listo, empaque individual *$500*. ¿Cuál es tu método de pago? (Efectivo, Tarjeta, Nequi, Daviplata o Bold)"
            ),
            self._example(
                "Es domicilio",
                "¡Con gusto! ¿Cuál es la dirección de entrega?"
            ),
            self._example(
                "La dirección es Calle 10 # 5-23",
                "Perfecto, anotamos *Calle 10 # 5-23*. ¿Qué toppings y salsas quieres en tu pedido?"
            ),
            self._example(
                "Para comer aquí",
                "¡Perfecto! Recuerda que la barra de toppings es libre, ponle todo lo que quieras. "
                "¿Cuál es tu método de pago?"
            ),
        ]

    def _gen_pagos(self) -> list[dict]:
        metodos = self._data["metodos_pago"]
        return [
            self._example(
                "Cómo puedo pagar?",
                f"Aceptamos: {', '.join(metodos)}. ¿Con cuál vas?"
            ),
            self._example(
                "Pago en efectivo",
                "¡Perfecto! Pago en efectivo anotado. ¿Confirmamos el pedido?"
            ),
            self._example(
                "Pago con Nequi",
                "¡Listo! Pago por Nequi. ¿Confirmamos el pedido?"
            ),
            self._example(
                "Pago con tarjeta",
                "Perfecto, tarjeta anotada. ¿Confirmamos el pedido?"
            ),
            self._example(
                "Tienen Daviplata?",
                "¡Sí! Aceptamos Daviplata, Nequi, Bold, tarjeta y efectivo. ¿Con cuál prefieres?"
            ),
        ]

    def _gen_adiciones_bebidas(self) -> list[dict]:
        return [
            self._example(
                "Puedo agrandar la bebida?",
                "¡Claro! Agrandar de 250ml a 500ml cuesta *$1.000* adicional. ¿Lo agrego?"
            ),
            self._example(
                "Qué bebidas tienen?",
                "Tenemos Bebida Mini ($3.000 / 250ml), Personal ($4.500 / 500ml) y Familiar ($6.500 / 1L-1.5L). "
                "Todas son productos CocaCola. ¿Cuál quieres?"
            ),
            self._example(
                "Tienen Sprite?",
                "¡Sí! Sprite está disponible en la *Bebida Personal* ($4.500). ¿La agrego a tu pedido?"
            ),
            self._example(
                "Quiero agregar un huevo frito",
                "¡Listo! Un *Huevo Frito* por *$1.500*. ¿Algo más?"
            ),
        ]

    def _gen_fuera_contexto(self) -> list[dict]:
        """Ejemplos de rechazo educado a preguntas fuera del restaurante."""
        return [
            self._example(
                "Cómo está el clima hoy?",
                "Jeje, eso sí no te puedo decir 😄 Pero sí te puedo tomar un pedido rico. ¿Qué se te antoja?"
            ),
            self._example(
                "Cuánto vale el dólar?",
                "Ese no es mi fuerte, pero sí sé cuánto vale una hamburguesa de res 😄 ¿Te pedimos algo?"
            ),
            self._example(
                "Me recomiendas una película?",
                "No soy experto en cine, ¡pero sí en hamburguesas! ¿Qué te provoca hoy?"
            ),
        ]

    # ── Generador principal ───────────────────────────────────────────────────

    def generate(self) -> list[dict]:
        """Genera todos los ejemplos del dataset."""
        self._examples = []
        self._examples.extend(self._gen_saludos())
        self._examples.extend(self._gen_preguntas_menu())
        self._examples.extend(self._gen_toppings())
        self._examples.extend(self._gen_pedidos())
        self._examples.extend(self._gen_modalidades())
        self._examples.extend(self._gen_pagos())
        self._examples.extend(self._gen_adiciones_bebidas())
        self._examples.extend(self._gen_fuera_contexto())
        random.shuffle(self._examples)
        return self._examples

    def save(self, path: str = DATASET_PATH) -> int:
        """Guarda el dataset en formato JSONL."""
        examples = self.generate()
        with open(path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"[DatasetGenerator] ✅ Dataset guardado: {path} ({len(examples)} ejemplos)")
        return len(examples)

# FINE-TUNING CON HUGGING FACE TRANSFORMERS
class FineTuner:
    """
    Fine-tunea un modelo de lenguaje usando el dataset generado.
    Usa DialoGPT-small (~117MB) que puede entrenarse en CPU.
    El modelo resultante queda guardado en ./finetuned_model/
    """

    def __init__(self, dataset_path: str = DATASET_PATH, output_dir: str = MODEL_OUTPUT_PATH):
        self._dataset_path = dataset_path
        self._output_dir = output_dir

    def _load_dependencies(self):
        #Importa las librerías de Hugging Face.
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                TrainingArguments,
                Trainer,
                DataCollatorForLanguageModeling,
            )
            from datasets import Dataset
            return AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling, Dataset
        except ImportError:
            raise ImportError(
                "Faltan dependencias de entrenamiento. Instala con:\n"
                "pip install transformers datasets accelerate torch"
            )

    def _load_dataset_hf(self, tokenizer, Dataset):
        #Carga y tokeniza el dataset JSONL.
        raw = []
        with open(self._dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line.strip())
                # Concatenamos prompt + completion como texto de entrenamiento
                text = item["prompt"] + item["completion"] + tokenizer.eos_token
                raw.append({"text": text})

        dataset = Dataset.from_list(raw)

        def tokenize(batch):
            return tokenizer(
                batch["text"],
                truncation=True,
                max_length=256,
                padding="max_length",
            )

        return dataset.map(tokenize, batched=True, remove_columns=["text"])

    def train(self):
        """Ejecuta el fine-tuning completo."""
        (AutoTokenizer, AutoModelForCausalLM,
         TrainingArguments, Trainer,
         DataCollatorForLanguageModeling, Dataset) = self._load_dependencies()

        print(f"\n[FineTuner] Cargando modelo base: {BASE_MODEL}")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

        print(f"[FineTuner] Cargando y tokenizando dataset: {self._dataset_path}")
        tokenized_dataset = self._load_dataset_hf(tokenizer, Dataset)

        # Dividir en train/eval (90/10)
        split = tokenized_dataset.train_test_split(test_size=0.1, seed=42)

        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        training_args = TrainingArguments(
            output_dir=self._output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            warmup_steps=10,
            weight_decay=0.01,
            logging_dir=os.path.join(self._output_dir, "logs"),
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            report_to="none",           # sin wandb
            
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=split["train"],
            eval_dataset=split["test"],
            data_collator=data_collator,
        )

        print(f"\n[FineTuner] 🚀 Iniciando entrenamiento ({len(split['train'])} ejemplos)...")
        print("[FineTuner] ⏳ Esto puede tomar 5-15 minutos en CPU. Paciencia...")
        trainer.train()

        print(f"\n[FineTuner] 💾 Guardando modelo fine-tuneado en: {self._output_dir}")
        trainer.save_model(self._output_dir)
        tokenizer.save_pretrained(self._output_dir)

        print(f"\n[FineTuner] ✅ Fine-tuning completado exitosamente!")
        print(f"[FineTuner] Modelo guardado en: {self._output_dir}")
        print(f"[FineTuner] Para usarlo en el bot, agrega USE_LOCAL_MODEL=true en tu .env")

# ENTRY POINT

def main():
    parser = argparse.ArgumentParser(description="Fine-tuning de Armelo Perro Bot")
    parser.add_argument("--generate", action="store_true", help="Solo genera el dataset JSONL")
    parser.add_argument("--train", action="store_true", help="Entrena el modelo (requiere dataset)")
    parser.add_argument("--both", action="store_true", help="Genera dataset y entrena (recomendado)")
    args = parser.parse_args()

    if not any([args.generate, args.train, args.both]):
        parser.print_help()
        return

    if args.generate or args.both:
        print("\n📝 Generando dataset de entrenamiento...")
        generator = DatasetGenerator()
        count = generator.save()
        print(f"   → {count} ejemplos generados en training_data.jsonl")

    if args.train or args.both:
        if not Path(DATASET_PATH).exists():
            print("❌ No se encontró training_data.jsonl. Ejecuta primero con --generate")
            return
        print("\n🤖 Iniciando fine-tuning del modelo...")
        tuner = FineTuner()
        tuner.train()


if __name__ == "__main__":
    main()
