"""
order.py - Clase para gestionar el pedido del cliente
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Modalidad(str, Enum):
    RESTAURANTE = "en el restaurante"
    PARA_LLEVAR = "para llevar"
    DOMICILIO = "domicilio"


class EstadoPedido(str, Enum):
    INICIANDO = "iniciando"
    TOMANDO_PEDIDO = "tomando_pedido"
    CONFIRMANDO = "confirmando"
    CONFIRMADO = "confirmado"
    FINALIZADO = "finalizado"


@dataclass
class ItemPedido:
    """Representa un producto dentro del pedido."""
    nombre: str
    combo: str
    precio: Optional[int]
    cantidad: int = 1
    toppings: list[str] = field(default_factory=list)
    salsas: list[str] = field(default_factory=list)
    adiciones: list[str] = field(default_factory=list)
    notas: str = ""

    def subtotal(self) -> int:
        return (self.precio or 0) * self.cantidad

    def __str__(self) -> str:
        precio_fmt = f"${self.precio:,.0f}".replace(",", ".") if self.precio else "Consultar"
        extras = []
        if self.toppings:
            extras.append(f"Toppings: {', '.join(self.toppings)}")
        if self.salsas:
            extras.append(f"Salsas: {', '.join(self.salsas)}")
        if self.adiciones:
            extras.append(f"Adiciones: {', '.join(self.adiciones)}")
        if self.notas:
            extras.append(f"Notas: {self.notas}")
        extra_str = " | " + " | ".join(extras) if extras else ""
        return f"x{self.cantidad} {self.nombre} {self.combo} ({precio_fmt}){extra_str}"


class Order:
    """Gestiona el estado completo del pedido de un cliente."""

    def __init__(self, cliente_id: str):
        self.cliente_id: str = cliente_id
        self.items: list[ItemPedido] = []
        self.modalidad: Optional[Modalidad] = None
        self.direccion: Optional[str] = None
        self.metodo_pago: Optional[str] = None
        self.estado: EstadoPedido = EstadoPedido.INICIANDO
        self.nombre_cliente: Optional[str] = None

    def agregar_item(self, item: ItemPedido) -> None:
        """Agrega un ítem al pedido."""
        self.items.append(item)

    def limpiar(self) -> None:
        """Reinicia el pedido."""
        self.items = []
        self.modalidad = None
        self.direccion = None
        self.metodo_pago = None
        self.estado = EstadoPedido.INICIANDO

    def total(self) -> int:
        """Calcula el total del pedido sin empaques."""
        return sum(item.subtotal() for item in self.items)

    def total_con_empaque(self) -> int:
        """Calcula el total incluyendo empaque si aplica domicilio/llevar."""
        total = self.total()
        if self.modalidad in (Modalidad.DOMICILIO, Modalidad.PARA_LLEVAR):
            total += 1000 if len(self.items) > 1 else 500
        return total

    def resumen(self) -> str:
        """Genera un resumen legible del pedido."""
        if not self.items:
            return "El pedido está vacío."

        lines = ["📋 *Resumen de tu pedido:*"]
        for item in self.items:
            lines.append(f"  ▸ {item}")

        lines.append(f"\n💰 *Subtotal:* ${self.total():,.0f}".replace(",", "."))

        if self.modalidad in (Modalidad.DOMICILIO, Modalidad.PARA_LLEVAR):
            empaque = 1000 if len(self.items) > 1 else 500
            lines.append(f"📦 *Empaque:* ${empaque:,.0f}".replace(",", "."))
            lines.append(f"💳 *Total:* ${self.total_con_empaque():,.0f}".replace(",", "."))
        else:
            lines.append(f"💳 *Total:* ${self.total():,.0f}".replace(",", "."))

        if self.modalidad:
            lines.append(f"🛵 *Modalidad:* {self.modalidad.value.capitalize()}")
        if self.direccion:
            lines.append(f"📍 *Dirección:* {self.direccion}")
        if self.metodo_pago:
            lines.append(f"💵 *Pago:* {self.metodo_pago}")

        return "\n".join(lines)

    def tiene_items(self) -> bool:
        return len(self.items) > 0

    def __repr__(self) -> str:
        return f"<Order cliente={self.cliente_id} items={len(self.items)} total={self.total_con_empaque()}>"
