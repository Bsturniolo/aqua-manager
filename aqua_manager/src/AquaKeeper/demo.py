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
