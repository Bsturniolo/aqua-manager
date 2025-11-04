# aqua_manager/src/AquaKeeper/servicios/inventario_service.py
from typing import Dict
from AquaKeeper.entidades.modelo import Producto, Stock
from AquaKeeper.patrones.observer.observer import Observable
from AquaKeeper.config.constantes import STOCK_MIN_LOCAL, STOCK_MIN_CLIENTE  # STOCK_MIN_CLIENTE por si querés usarlo luego

class EventoStock:
    def __init__(self, origen: str, sku: str, nuevo: float, minimo: float):
        self.origen = origen         # "local" o "cliente:<dni>"
        self.sku = sku
        self.nuevo = nuevo
        self.minimo = minimo

class InventarioLocal(Observable[EventoStock]):
    def __init__(self):
        super().__init__()
        self.productos: Dict[str, Producto] = {}  # sku -> Producto
        self.stock = Stock()                      # sku -> cantidad

    def registrar_producto(self, p: Producto, cantidad_inicial: float=0.0) -> None:
        self.productos[p.sku] = p
        if cantidad_inicial:
            self.stock.disponer(p.sku, cantidad_inicial)

    def _resolver_sku(self, sku_o_tipo: str) -> str:
        if sku_o_tipo in self.productos:
            return sku_o_tipo
        # si vino un tipo, tomamos el primer SKU de ese tipo
        for sku, prod in self.productos.items():
            if prod.tipo == sku_o_tipo:
                return sku
        # si no existe, devolvemos tal cual (dejará fallar donde corresponda)
        return sku_o_tipo

    def reponer(self, sku_o_tipo: str, cant: float) -> None:
        sku = self._resolver_sku(sku_o_tipo)
        self.stock.disponer(sku, cant)

    def obtener(self, sku: str) -> Producto:
        return self.productos[sku]

    def disponible(self, sku_o_tipo: str) -> float:
        sku = self._resolver_sku(sku_o_tipo)
        return self.stock.disponible(sku)

    def descontar(self, sku_o_tipo: str, cant: float) -> None:
        sku = self._resolver_sku(sku_o_tipo)
        self.stock.descontar(sku, cant)
        if self.disponible(sku) <= STOCK_MIN_LOCAL:
            self.notificar(EventoStock("local", sku, self.disponible(sku), STOCK_MIN_LOCAL))
