"""
Archivo integrador generado automaticamente
Directorio: /home/bautista/aqua_manager/src/AquaKeeper/servicios
Fecha: 2025-11-04 16:32:00
Total de archivos integrados: 4
"""

# ================================================================================
# ARCHIVO 1/4: __init__.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/servicios/__init__.py
# ================================================================================



# ================================================================================
# ARCHIVO 2/4: inventario_service.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/servicios/inventario_service.py
# ================================================================================

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


# ================================================================================
# ARCHIVO 3/4: pileta_service.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/servicios/pileta_service.py
# ================================================================================

# aqua_manager/src/AquaKeeper/servicios/pileta_service.py
from __future__ import annotations
from typing import Dict, List, Tuple
from AquaKeeper.entidades.modelo import Pileta, Cliente, Visita
from AquaKeeper.patrones.strategy.dosificacion import DosificacionStrategy
from AquaKeeper.config.constantes import PH_IDEAL_MIN, PH_IDEAL_MAX, TURBIDEZ_MAX_PERMITIDA, ALGAS_UMBRAL_ALERTA, STOCK_MIN_CLIENTE

class PiletaService:
    def __init__(self):
        self.piletas: Dict[str, Pileta] = {}  # id -> Pileta
        self.clientes: Dict[str, Cliente] = {}  # dni -> Cliente
        self.visitas: List[Visita] = []

    # Altas
    def registrar_cliente(self, c: Cliente) -> None:
        self.clientes[c.dni] = c

    def registrar_pileta(self, p: Pileta) -> None:
        self.piletas[p.id_pileta] = p

    # Cálculo de % “estado del agua” (0..100)
    def estado_agua_porcentual(self, p: Pileta) -> float:
        # toy model simple: penaliza salir del rango pH y turbidez/alga altas
        score = 100.0
        if not (PH_IDEAL_MIN <= p.ph <= PH_IDEAL_MAX):
            score -= 25.0
        if p.turbidez > TURBIDEZ_MAX_PERMITIDA:
            score -= 25.0
        if p.algas > ALGAS_UMBRAL_ALERTA:
            score -= 50.0
        return max(0.0, min(100.0, score))

    # % de cobertura por producto (en el hogar del cliente) vs lo que requeriría hoy una dosificación
    def cobertura_productos_cliente(self, dni: str, p: Pileta, strat: DosificacionStrategy) -> Dict[str, float]:
        c = self.clientes[dni]
        dosis = strat.calcular_dosis(p)  # tipo -> cant requerida
        cobertura = {}
        for tipo, cantidad_req in dosis.items():
            # asumimos SKU = tipo para simplificar (podés mapear tipos->SKUs reales)
            disponible = c.stock.disponible(tipo)
            porc = 100.0 if cantidad_req == 0 else max(0.0, min(100.0, (disponible / cantidad_req) * 100.0))
            cobertura[tipo] = round(porc, 1)
        return cobertura

    # Qué me falta en la casa del cliente para aplicar la acción
    def faltantes_cliente(self, dni: str, p: Pileta, strat: DosificacionStrategy) -> Dict[str, float]:
        c = self.clientes[dni]
        dosis = strat.calcular_dosis(p)
        faltantes = {}
        for tipo, req in dosis.items():
            disp = c.stock.disponible(tipo)
            if disp < req:
                faltantes[tipo] = round(req - disp, 2)
        return faltantes

    # Registra una visita y dice si “debo ir”
    def evaluar_visita(self, id_pileta: str, razon: str, strat: DosificacionStrategy) -> Tuple[Visita, bool]:
        p = self.piletas[id_pileta]
        c = self.clientes[p.cliente_dni]
        estado = self.estado_agua_porcentual(p)
        faltan = self.faltantes_cliente(c.dni, p, strat)
        debo_ir = (estado < 70.0) or bool(faltan)
        v = Visita(id_pileta=id_pileta, razon=razon, realizado=False,
                   observacion=f"Estado agua {estado:.1f}%. Faltantes: {faltan}")
        self.visitas.append(v)
        return v, debo_ir

    # Salud de “productos de la pileta” (porcentajes deseados por tipo respecto a un “target” de mantenimiento)
    def salud_productos_en_pileta(self, p: Pileta, strat: DosificacionStrategy) -> Dict[str, float]:
        # Interpretación: si HOY me pide X de cada producto, 0% = nada, 100% = tengo al menos X “en mano”.
        dosis = strat.calcular_dosis(p)
        res = {}
        for tipo, req in dosis.items():
            # “productos en pileta” lo aproximamos como 0 (requiere medir ppm real).
            # Para mostrar barra 0..100, aquí dejamos 0; se puede integrar sensor/medición real a futuro.
            res[tipo] = 0.0 if req > 0 else 100.0
        return res


# ================================================================================
# ARCHIVO 4/4: registro_service.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/servicios/registro_service.py
# ================================================================================

# aqua_manager/src/AquaKeeper/servicios/registro_service.py
from dataclasses import dataclass
from pathlib import Path
import pickle

@dataclass
class RegistroOperacion:
    descripcion: str
    datos: dict

class RegistroService:
    base = Path("./data")

    def guardar(self, nombre: str, reg: RegistroOperacion) -> Path:
        self.base.mkdir(exist_ok=True)
        p = self.base / f"{nombre}.dat"
        with open(p, "wb") as f:
            pickle.dump(reg, f)
        return p


