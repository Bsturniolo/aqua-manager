"""
INTEGRADOR FINAL - CONSOLIDACION COMPLETA DEL PROYECTO
============================================================================
Directorio raiz: /home/bautista/aqua_manager/src/AquaKeeper
Fecha de generacion: 2025-11-04 16:32:00
Total de archivos integrados: 14
Total de directorios procesados: 7
============================================================================
"""

# ==============================================================================
# TABLA DE CONTENIDOS
# ==============================================================================

# DIRECTORIO: .
#   1. __init__.py
#   2. __main__.py
#   3. demo.py
#
# DIRECTORIO: config
#   4. __init__.py
#   5. configuracion.py
#   6. constantes.py
#
# DIRECTORIO: entidades
#   7. modelo.py
#
# DIRECTORIO: patrones/factory
#   8. producto_factory.py
#
# DIRECTORIO: patrones/observer
#   9. observer.py
#
# DIRECTORIO: patrones/strategy
#   10. dosificacion.py
#
# DIRECTORIO: servicios
#   11. __init__.py
#   12. inventario_service.py
#   13. pileta_service.py
#   14. registro_service.py
#



################################################################################
# DIRECTORIO: .
################################################################################

# ==============================================================================
# ARCHIVO 1/14: __init__.py
# Directorio: .
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/__init__.py
# ==============================================================================



# ==============================================================================
# ARCHIVO 2/14: __main__.py
# Directorio: .
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/__main__.py
# ==============================================================================

from .demo import demo
if __name__ == "__main__":
    demo()


# ==============================================================================
# ARCHIVO 3/14: demo.py
# Directorio: .
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/demo.py
# ==============================================================================

from __future__ import annotations
from typing import Optional, Dict, Callable
from AquaKeeper.entidades.modelo import Cliente, Pileta, Producto
from AquaKeeper.patrones.factory.producto_factory import ProductoFactory
from AquaKeeper.patrones.strategy.dosificacion import (
    EstrategiaMantenimiento, EstrategiaChoque, EstrategiaAlguicida, EstrategiaAntisarro
)
from AquaKeeper.patrones.observer.observer import Observer
from AquaKeeper.servicios.inventario_service import InventarioLocal, EventoStock
from AquaKeeper.servicios.pileta_service import PiletaService
from AquaKeeper.servicios.registro_service import RegistroService, RegistroOperacion
from AquaKeeper.config.constantes import (
    PISCINA_CHICA_L, PISCINA_MEDIANA_L, PISCINA_GRANDE_L,
    STOCK_MIN_CLIENTE, STOCK_MIN_LOCAL
)

# ---------- Singleton: formateo (sin lambdas) ----------
def _fmt_producto(p: Producto) -> str:
    return f"{p.nombre} [{p.tipo}] ({p.presentacion})"

class ProductoFormatterRegistry:
    _inst: Optional["ProductoFormatterRegistry"] = None
    def __init__(self):
        self._fmt: Dict[type, Callable[[Producto], str]] = { Producto: _fmt_producto }
    @classmethod
    def instance(cls) -> "ProductoFormatterRegistry":
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst
    def mostrar(self, p: Producto) -> str:
        return self._fmt.get(type(p), _fmt_producto)(p)

# ---------- Observer: alertas de stock ----------
class Alertas(Observer[EventoStock]):
    def actualizar(self, ev: EventoStock) -> None:
        print(f"[ALERTA STOCK] origen={ev.origen} sku={ev.sku} nuevo={ev.nuevo} (mín {ev.minimo})")

# ---------- DEMO ----------
def demo():
    print("="*70); print(" DEMO: AquaKeeper - Gestión de Piletas "); print("="*70)
    regfmt = ProductoFormatterRegistry.instance()

    # 1) Inventario local + productos del mercado
    inv = InventarioLocal()
    inv.suscribir(Alertas())

    productos = [
        ProductoFactory.crear("cloro-granulado", "CL-GR-1", "Cloro Granulado Premium", "1kg"),
        ProductoFactory.crear("cloro-pastilla",  "CL-PA-2", "Pastillas de Cloro 200g", "200g"),
        ProductoFactory.crear("clarificador",    "CL-AR-3", "Clarificador Ultra", "1L"),
        ProductoFactory.crear("alguicida",       "AL-GI-4", "Alguicida Shock", "1L"),
        ProductoFactory.crear("antisarro",       "AN-SA-5", "Antisarro Plus", "1L"),
    ]
    for p in productos:
        inv.registrar_producto(p, cantidad_inicial=5)  # 5 unidades
        print("Producto:", regfmt.mostrar(p))

    print(f"\n[INFO] Stock local mínimo = {STOCK_MIN_LOCAL}, stock cliente mínimo = {STOCK_MIN_CLIENTE}")

    # 2) Clientes + piletas (tus clientes con su stock en casa)
    svc = PiletaService()
    c1 = Cliente(dni="111", nombre="Laura",  direccion="San Martín 123")
    c2 = Cliente(dni="222", nombre="Diego",  direccion="Belgrano 456")

    # El cliente guarda stock por TIPO como “sku” simple (tipo==clave)
    for tipo in ["cloro-granulado","clarificador","alguicida","antisarro","cloro-pastilla"]:
        c1.stock.disponer(tipo, 50.0)  # 50 g/ml/pastillas (ejemplo)
        c2.stock.disponer(tipo, 10.0)  # 10 g/ml/pastillas (bajo para ver faltantes)

    svc.registrar_cliente(c1)
    svc.registrar_cliente(c2)

    p1 = Pileta(id_pileta="P-CHICA",   litros=PISCINA_CHICA_L,  cliente_dni=c1.dni, ph=7.6, turbidez=15.0, algas=0.2)
    p2 = Pileta(id_pileta="P-MED",     litros=PISCINA_MEDIANA_L,cliente_dni=c1.dni, ph=7.1, turbidez=35.0, algas=0.6)
    p3 = Pileta(id_pileta="P-GRANDE",  litros=PISCINA_GRANDE_L, cliente_dni=c2.dni, ph=7.5, turbidez=12.0, algas=0.0)

    for pp in (p1,p2,p3): svc.registrar_pileta(pp)

    # 3) Estrategias según necesidad (Strategy)
    s_mant   = EstrategiaMantenimiento()
    s_choque = EstrategiaChoque()
    s_alg    = EstrategiaAlguicida()
    s_sarro  = EstrategiaAntisarro()

    casos = [
        ("mantenimiento", p1, s_mant),
        ("choque",        p2, s_choque),
        ("mantenimiento", p3, s_mant),
    ]

    print("\nESTADO Y NECESIDADES:")
    for razon, pile, strat in casos:
        est = svc.estado_agua_porcentual(pile)
        cob = svc.cobertura_productos_cliente(pile.cliente_dni, pile, strat)   # % cobertura con stock del cliente
        falt= svc.faltantes_cliente(pile.cliente_dni, pile, strat)             # faltantes en casa del cliente
        sal = svc.salud_productos_en_pileta(pile, strat)                        # 0..100 (placeholder)

        print(f"- Pileta {pile.id_pileta} ({pile.litros} L) de cliente {pile.cliente_dni}")
        print(f"  Estado agua: {est:.1f}%  |  acción: {razon}")
        print(f"  % productos en PILETA (estimado hoy): {sal}")
        print(f"  % productos en CASA del cliente (cobertura vs dosis): {cob}")
        print(f"  Faltantes para aplicar hoy: {falt}")

        visita, debo_ir = svc.evaluar_visita(pile.id_pileta, razon, strat)
        print(f"  Registro visita: {'DEBO IR' if debo_ir else 'OK'} → {visita.observacion}")

    # 4) Simular “venta” desde tu local (descontar inventario) — usando TIPO -> SKU
    print("\nSIMULACIÓN: preparo kit para la pileta P-MED (choque) del cliente 111")

    # Mapa TIPO -> SKU real en el inventario local
    map_tipo_sku = {p.tipo: p.sku for p in productos}

    dosis_p2 = s_choque.calcular_dosis(p2)   # tipo->cantidad requerida hoy (no usamos la cantidad para el descuento simple)
    for tipo, _cant in dosis_p2.items():
        sku = map_tipo_sku.get(tipo)
        if not sku:
            print(f"  [AVISO] No tengo SKU mapeado para el tipo '{tipo}', salto.")
            continue
        try:
            inv.descontar(sku, 1.0)  # ejemplo simple: 1 unidad por ítem
            print(f"  Descuento local: {tipo} (sku={sku}) x 1 unidad | stock ahora={inv.disponible(sku)}")
        except ValueError as e:
            print(f"  [STOCK] {e}")

    # 5) Persistencia de un resumen
    salida = {
        "piletas": [p1.__dict__, p2.__dict__, p3.__dict__],
        "visitas": [v.__dict__ for v in svc.visitas],
    }
    pfile = RegistroService().guardar("resumen_aquakeeper", RegistroOperacion("resumen", salida))
    print(f"\n[OK] Resumen persistido en {pfile}")

    print("="*70); print("EJEMPLO COMPLETADO (AquaKeeper)")
    print("[OK] SINGLETON | [OK] FACTORY | [OK] OBSERVER | [OK] STRATEGY")
    print("="*70)



################################################################################
# DIRECTORIO: config
################################################################################

# ==============================================================================
# ARCHIVO 4/14: __init__.py
# Directorio: config
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/config/__init__.py
# ==============================================================================



# ==============================================================================
# ARCHIVO 5/14: configuracion.py
# Directorio: config
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/config/configuracion.py
# ==============================================================================

# aqua_manager/src/AquaKeeper/config/constantes.py
# Parámetros globales de negocio y umbrales

# Tamaños típicos (L)
PISCINA_CHICA_L   = 12000
PISCINA_MEDIANA_L = 25000
PISCINA_GRANDE_L  = 45000

# Dosis por 10.000 L (referencia)
# (valores estimativos tipo ficha técnica — ajustá a tu cartera real)
DOSIS_CLORO_MANTENIMIENTO_G_10K    = 30     # gr/10kL (diario/mantenimiento)
DOSIS_CLORO_CHOQUE_G_10K           = 120    # gr/10kL (choque)
DOSIS_CLARIFICADOR_ML_10K          = 40     # ml/10kL
DOSIS_ALGUICIDA_ML_10K             = 25     # ml/10kL
DOSIS_ANTISARRO_ML_10K             = 35     # ml/10kL

# Umbrales para decisiones
PH_IDEAL_MIN = 7.2
PH_IDEAL_MAX = 7.6
TURBIDEZ_MAX_PERMITIDA = 30.0   # NTU equivalente (simulado)
ALGAS_UMBRAL_ALERTA    = 0.5    # 0..1

# Stock: mínimos
STOCK_MIN_LOCAL = 2         # en tu local (unidades)
STOCK_MIN_CLIENTE = 1       # cliente suele tener 1 o 2


# ==============================================================================
# ARCHIVO 6/14: constantes.py
# Directorio: config
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/config/constantes.py
# ==============================================================================

PISCINA_CHICA_L   = 12000
PISCINA_MEDIANA_L = 25000
PISCINA_GRANDE_L  = 45000

DOSIS_CLORO_MANTENIMIENTO_G_10K = 30
DOSIS_CLORO_CHOQUE_G_10K        = 120
DOSIS_CLARIFICADOR_ML_10K       = 40
DOSIS_ALGUICIDA_ML_10K          = 25
DOSIS_ANTISARRO_ML_10K          = 35

PH_IDEAL_MIN = 7.2
PH_IDEAL_MAX = 7.6
TURBIDEZ_MAX_PERMITIDA = 30.0
ALGAS_UMBRAL_ALERTA    = 0.5

STOCK_MIN_LOCAL   = 2
STOCK_MIN_CLIENTE = 1



################################################################################
# DIRECTORIO: entidades
################################################################################

# ==============================================================================
# ARCHIVO 7/14: modelo.py
# Directorio: entidades
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/entidades/modelo.py
# ==============================================================================

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



################################################################################
# DIRECTORIO: patrones/factory
################################################################################

# ==============================================================================
# ARCHIVO 8/14: producto_factory.py
# Directorio: patrones/factory
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/patrones/factory/producto_factory.py
# ==============================================================================

# aqua_manager/src/AquaKeeper/patrones/factory/producto_factory.py
from AquaKeeper.entidades.modelo import Producto

class ProductoFactory:
    @staticmethod
    def _crear_cloro_granulado(sku: str, nombre: str, presentacion: str="1kg") -> Producto:
        return Producto(sku, nombre, "cloro-granulado", "g", presentacion)

    @staticmethod
    def _crear_cloro_pastilla(sku: str, nombre: str, presentacion: str="200g") -> Producto:
        return Producto(sku, nombre, "cloro-pastilla", "pastillas", presentacion)

    @staticmethod
    def _crear_clarificador(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "clarificador", "ml", presentacion)

    @staticmethod
    def _crear_alguicida(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "alguicida", "ml", presentacion)

    @staticmethod
    def _crear_antisarro(sku: str, nombre: str, presentacion: str="1L") -> Producto:
        return Producto(sku, nombre, "antisarro", "ml", presentacion)

    @staticmethod
    def crear(tipo: str, sku: str, nombre: str, presentacion: str="") -> Producto:
        dispatch = {
            "cloro-granulado": ProductoFactory._crear_cloro_granulado,
            "cloro-pastilla":  ProductoFactory._crear_cloro_pastilla,
            "clarificador":    ProductoFactory._crear_clarificador,
            "alguicida":       ProductoFactory._crear_alguicida,
            "antisarro":       ProductoFactory._crear_antisarro,
        }
        key = (tipo or "").lower()
        if key not in dispatch:
            raise ValueError(f"Tipo de producto desconocido: {tipo}")
        return dispatch[key](sku, nombre, presentacion or "")



################################################################################
# DIRECTORIO: patrones/observer
################################################################################

# ==============================================================================
# ARCHIVO 9/14: observer.py
# Directorio: patrones/observer
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/patrones/observer/observer.py
# ==============================================================================

# aqua_manager/src/AquaKeeper/patrones/observer/observer.py
from typing import Generic, List, TypeVar
T = TypeVar("T")

class Observer(Generic[T]):
    def actualizar(self, valor: T) -> None:
        raise NotImplementedError

class Observable(Generic[T]):
    def __init__(self) -> None:
        self._obs: List[Observer[T]] = []

    # nombres "clásicos"
    def suscribir(self, o: "Observer[T]") -> None: self._obs.append(o)
    def desuscribir(self, o: "Observer[T]") -> None: self._obs = [x for x in self._obs if x is not o]
    def notificar(self, v: T) -> None:
        for o in list(self._obs):
            o.actualizar(v)

    # Aliases tipo rúbrica/README
    def agregar_observador(self, o: "Observer[T]")->None: self.suscribir(o)
    def eliminar_observador(self, o: "Observer[T]")->None: self.desuscribir(o)
    def notificar_observadores(self, e: T)->None: self.notificar(e)



################################################################################
# DIRECTORIO: patrones/strategy
################################################################################

# ==============================================================================
# ARCHIVO 10/14: dosificacion.py
# Directorio: patrones/strategy
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/patrones/strategy/dosificacion.py
# ==============================================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict
from AquaKeeper.entidades.modelo import Pileta
from AquaKeeper.config.constantes import (
    DOSIS_CLORO_MANTENIMIENTO_G_10K, DOSIS_CLORO_CHOQUE_G_10K,
    DOSIS_CLARIFICADOR_ML_10K, DOSIS_ALGUICIDA_ML_10K, DOSIS_ANTISARRO_ML_10K
)

class DosificacionStrategy(ABC):
    @abstractmethod
    def calcular_dosis(self, p: Pileta) -> Dict[str, float]: ...

def _escala_por_litros(base_por_10k: float, litros: int) -> float:
    return round(base_por_10k * (litros / 10000.0), 2)

class EstrategiaMantenimiento(DosificacionStrategy):
    def calcular_dosis(self, p: Pileta) -> Dict[str, float]:
        return {
            "cloro-granulado": _escala_por_litros(DOSIS_CLORO_MANTENIMIENTO_G_10K, p.litros),
            "clarificador":    _escala_por_litros(DOSIS_CLARIFICADOR_ML_10K, p.litros),
        }

class EstrategiaChoque(DosificacionStrategy):
    def calcular_dosis(self, p: Pileta) -> Dict[str, float]:
        return {
            "cloro-granulado": _escala_por_litros(DOSIS_CLORO_CHOQUE_G_10K, p.litros),
            "clarificador":    _escala_por_litros(DOSIS_CLARIFICADOR_ML_10K*2, p.litros),
            "alguicida":       _escala_por_litros(DOSIS_ALGUICIDA_ML_10K, p.litros),
        }

class EstrategiaAlguicida(DosificacionStrategy):
    def calcular_dosis(self, p: Pileta) -> Dict[str, float]:
        return { "alguicida": _escala_por_litros(DOSIS_ALGUICIDA_ML_10K, p.litros) }

class EstrategiaAntisarro(DosificacionStrategy):
    def calcular_dosis(self, p: Pileta) -> Dict[str, float]:
        return { "antisarro": _escala_por_litros(DOSIS_ANTISARRO_ML_10K, p.litros) }



################################################################################
# DIRECTORIO: servicios
################################################################################

# ==============================================================================
# ARCHIVO 11/14: __init__.py
# Directorio: servicios
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/servicios/__init__.py
# ==============================================================================



# ==============================================================================
# ARCHIVO 12/14: inventario_service.py
# Directorio: servicios
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/servicios/inventario_service.py
# ==============================================================================

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


# ==============================================================================
# ARCHIVO 13/14: pileta_service.py
# Directorio: servicios
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/servicios/pileta_service.py
# ==============================================================================

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


# ==============================================================================
# ARCHIVO 14/14: registro_service.py
# Directorio: servicios
# Ruta completa: /home/bautista/aqua_manager/src/AquaKeeper/servicios/registro_service.py
# ==============================================================================

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



################################################################################
# FIN DEL INTEGRADOR FINAL
# Total de archivos: 14
# Generado: 2025-11-04 16:32:00
################################################################################
