# aqua_manager/src/AquaKeeper/entidades/modelo.py
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Producto:
    sku: str
    nombre: str
    tipo: str            # "cloro-granulado", "cloro-pastilla", "clarificador", "alguicida", "antisarro"
    unidad: str          # "g" o "ml" o "pastillas"
    presentacion: str = ""  # opcional, por ejemplo "1kg", "1L"

@dataclass
class Stock:
    cantidades: Dict[str, float] = field(default_factory=dict)  # sku -> cantidad (en unidad del producto)

    def disponer(self, sku: str, cant: float) -> None:
        self.cantidades[sku] = self.cantidades.get(sku, 0.0) + cant

    def descontar(self, sku: str, cant: float) -> None:
        actual = self.cantidades.get(sku, 0.0)
        if cant > actual:
            raise ValueError(f"Stock insuficiente para {sku} (tiene {actual}, pide {cant})")
        self.cantidades[sku] = actual - cant

    def disponible(self, sku: str) -> float:
        return self.cantidades.get(sku, 0.0)

@dataclass
class Pileta:
    id_pileta: str
    litros: int
    cliente_dni: str
    ph: float = 7.4
    turbidez: float = 10.0     # más bajo, mejor
    algas: float = 0.0         # 0..1 (0 = nada, 1 = mucha)

@dataclass
class Cliente:
    dni: str
    nombre: str
    direccion: str
    # stock del cliente (lo que tiene en su casa)
    stock: Stock = field(default_factory=Stock)

@dataclass
class Visita:
    id_pileta: str
    razon: str                # "mantenimiento", "choque", "alguicida", etc.
    realizado: bool
    observacion: str = ""
