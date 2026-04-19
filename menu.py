#menu.py - Clase para cargar y representar el menú de Armelo Perro
import json
from typing import Optional
from config import Config


class MenuItem:
    #Representa un ítem individual del menú.

    def __init__(self, nombre: str, combo: str, precio: Optional[int], descripcion: str):
        self.nombre = nombre
        self.combo = combo
        self.precio = precio
        self.descripcion = descripcion

    def precio_formateado(self) -> str:
        if self.precio is None:
            return "Consultar precio"
        return f"${self.precio:,.0f}".replace(",", ".")

    def __str__(self) -> str:
        return f"{self.nombre} ({self.combo}) - {self.precio_formateado()}: {self.descripcion}"


class Menu:
    #Carga y provee acceso estructurado al menú completo del restaurante.

    def __init__(self, path: str = Config.MENU_DATA_PATH):
        self._path = path
        self._data: dict = {}
        self.items: list[MenuItem] = []
        self._load()

    def _load(self) -> None:
        """Carga el menú desde el archivo JSON."""
        with open(self._path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._parse_items()

    def _parse_items(self) -> None:
        """Convierte el JSON en objetos MenuItem."""
        menu = self._data.get("menu", {})

        # Hamburguesas
        for h in menu.get("hamburguesas", []):
            for opcion in h.get("opciones", []):
                self.items.append(
                    MenuItem(h["nombre"], opcion["combo"], opcion.get("precio"), opcion["descripcion"])
                )

        # Hotdogs
        for hd in menu.get("hotdogs", []):
            for opcion in hd.get("opciones", []):
                self.items.append(
                    MenuItem(hd["nombre"], opcion["combo"], opcion.get("precio"), opcion["descripcion"])
                )

        # Porciones
        for p in menu.get("porciones", []):
            self.items.append(MenuItem(p["nombre"], p["combo"], p.get("precio"), p["descripcion"]))

        # Adiciones
        for a in menu.get("adiciones", []):
            self.items.append(MenuItem(a["nombre"], "Adición", a.get("precio"), a["descripcion"]))

        # Bebidas
        for b in menu.get("bebidas", []):
            self.items.append(MenuItem(b["nombre"], "Bebida", b.get("precio"), b["descripcion"]))

        # Domicilio
        for d in menu.get("domicilio", []):
            self.items.append(MenuItem(d["nombre"], "Domicilio", d.get("precio"), d["descripcion"]))

    def to_prompt_text(self) -> str:
        #Convierte el menú completo a texto legible para el system prompt.
        data = self._data
        lines = [
            f"RESTAURANTE: {data['restaurante']}",
            f"DESCRIPCIÓN: {data['descripcion']}",
            f"HORARIO: {data['horario']}",
            f"MÉTODOS DE PAGO: {', '.join(data['metodos_pago'])}",
            f"MODALIDADES: {', '.join(data['modalidades'])}",
            "",
            "=== BARRA DE TOPPINGS (¡GRATIS, TODO LO QUE QUIERAS!) ===",
            f"Toppings: {', '.join(data['barra_toppings']['toppings'])}",
            f"Salsas: {', '.join(data['barra_toppings']['salsas'])}",
            f"NOTA: {data['nota_barra']}",
            "",
            "=== MENÚ ===",
        ]

        menu = data["menu"]

        lines.append("\n--- HAMBURGUESAS ---")
        for h in menu["hamburguesas"]:
            for op in h["opciones"]:
                precio = f"${op['precio']:,.0f}".replace(",", ".") if op.get("precio") else "Consultar precio"
                lines.append(f"• {h['nombre']} {op['combo']}: {precio} | {op['descripcion']}")

        lines.append("\n--- HOTDOGS ---")
        for hd in menu["hotdogs"]:
            for op in hd["opciones"]:
                precio = f"${op['precio']:,.0f}".replace(",", ".") if op.get("precio") else "Consultar precio"
                lines.append(f"• Hotdog {op['combo']}: {precio} | {op['descripcion']}")

        lines.append("\n--- PORCIONES INDIVIDUALES ---")
        for p in menu["porciones"]:
            lines.append(f"• {p['nombre']} ({p['combo']}): ${p['precio']:,.0f} | {p['descripcion']}".replace(",", "."))

        lines.append("\n--- ADICIONES (precio c/u) ---")
        for a in menu["adiciones"]:
            lines.append(f"• {a['nombre']}: ${a['precio']:,.0f} | {a['descripcion']}".replace(",", "."))

        lines.append("\n--- BEBIDAS ---")
        for b in menu["bebidas"]:
            lines.append(f"• {b['nombre']}: ${b['precio']:,.0f} | {b['descripcion']}".replace(",", "."))

        lines.append("\n--- EMPAQUES DOMICILIO ---")
        for d in menu["domicilio"]:
            lines.append(f"• {d['nombre']}: ${d['precio']:,.0f} | {d['descripcion']}".replace(",", "."))

        return "\n".join(lines)

    @property
    def restaurante(self) -> str:
        return self._data.get("restaurante", "Armelo Perro")
