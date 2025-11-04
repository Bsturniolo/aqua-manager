# AquaKeeper – Gestión Integral de Piletas 🏊‍♂️✨

> **Tu asistente para mantener piletas perfectas**: calcula dosis inteligentes, controla stocks (tu local + los clientes), registra visitas y te dice cuándo **“DEBO IR”**. Todo con arquitectura limpia y **4 patrones de diseño** (Strategy, Factory, Observer, Singleton).

---

## 📌 Idea general

AquaKeeper resuelve el día a día de un negocio real de mantenimiento de piletas:

- **Dominios clave**
  - **Cliente** y **Pileta** (litros, pH, turbidez, algas).
  - **Productos**: cloro granulado/pastillas, clarificador, alguicida, antisarro.
  - **Stock** en tu **local** y **stock en casa del cliente**.
  - **Dosis recomendada** según escenario: mantenimiento, choque, alguicida, antisarro.
  - **Visitas**: registro + sugerencia si **DEBO IR** (por estado del agua y faltantes).

- **Patrones implementados**
  - **Strategy** → dosificación por estrategia.
  - **Factory** → alta homogénea de productos.
  - **Observer** → alertas de stock del local.
  - **Singleton** → formateo consistente de productos en consola.

---

## 🗂️ Estructura del proyecto

aqua_manager/
├─ README.md
├─ Makefile
├─ data/                       # salidas (persistencia simple)
│  └─ resumen_aquakeeper.dat
└─ src/
   ├─ main.py                  # entrypoint clásico: python3 src/main.py
   └─ AquaKeeper/
      ├─ __main__.py           # entrypoint como módulo: PYTHONPATH=src python3 -m AquaKeeper
      ├─ demo.py               # orquesta la demo: productos, clientes, piletas, visitas, persistencia
      ├─ config/
      │  └─ constantes.py      # parámetros de negocio (dosis base, umbrales, tamaños, etc.)
      ├─ entidades/
      │  └─ modelo.py          # dataclasses: Producto, Stock, Pileta, Cliente, Visita
      ├─ patrones/
      │  ├─ factory/
      │  │  └─ producto_factory.py   # Factory de productos
      │  ├─ strategy/
      │  │  └─ dosificacion.py       # Strategy de dosis (mantenimiento/choque/alguicida/antisarro)
      │  └─ observer/
      │     └─ observer.py           # Observable/Observer (alertas)
      └─ servicios/
         ├─ inventario_service.py    # Inventario del local (+ Observer de stock)
         ├─ pileta_service.py        # Lógica de estado del agua, faltantes, visitas
         └─ registro_service.py      # Persistencia simple (pickle)

🧪 Productos y dosis (detalles rápidos)
Tipos y unidades:
cloro-granulado → gramos (g)
cloro-pastilla → pastillas
clarificador → mililitros (ml)
alguicida → mililitros (ml)
antisarro → mililitros (ml)
Dosis base por 10.000 L (ajustables en config/constantes.py):
Mantenimiento: cloro-granulado = 30 g, clarificador = 40 ml
Choque: cloro-granulado = 120 g, clarificador = 80 ml, alguicida = 25 ml
Antisarro: antisarro = 35 ml
Alguicida: alguicida = 25 ml
Las dosis escalan proporcionalmente al volumen de la pileta.

🧠 Lógica de negocio (core)
Estado del agua (0..100 %)
En servicios/pileta_service.py:
Parte de 100 y penaliza si:
pH fuera de [7.2, 7.6] → −25
Turbidez > umbral → −25
Algas > umbral → −50
Resultado delimitado entre 0 y 100.
Cobertura en casa del cliente (%)
Compara stock del cliente vs la dosis requerida hoy por estrategia.
Devuelve % por tipo: si el cliente tiene lo necesario → ~100%; si no, menos.
Útil para saber qué falta llevar.
Faltantes y visita
Con faltantes_cliente(...) obtengo un dict de tipo → cantidad que falta.
Con evaluar_visita(...) decide si DEBO IR (si el estado < 70% o hay faltantes).
Además registra una Visita con observación (queda también en el resumen persistido).
Descuento de stock (local)
En la demo, se arma un kit y se descuenta por SKU del inventario del local.
Mapeo tipo → SKU para bajar stock correctamente.
Persistencia
registro_service.py guarda un resumen (piletas + visitas) en data/resumen_aquakeeper.dat.

🖨️ ¿Qué imprime cuando lo corrés?

Ejemplo real (resumido):
======================================================================
 DEMO: AquaKeeper - Gestión de Piletas 
======================================================================
Producto: Cloro Granulado Premium [cloro-granulado] (1kg)
Producto: Pastillas de Cloro 200g [cloro-pastilla] (200g)
Producto: Clarificador Ultra [clarificador] (1L)
Producto: Alguicida Shock [alguicida] (1L)
Producto: Antisarro Plus [antisarro] (1L)

[INFO] Stock local mínimo = 2, stock cliente mínimo = 1

ESTADO Y NECESIDADES:
- Pileta P-CHICA (12000 L) de cliente 111
  Estado agua: 100.0%  |  acción: mantenimiento
  % productos en PILETA (estimado hoy): {'cloro-granulado': 0.0, 'clarificador': 0.0}
  % productos en CASA del cliente (cobertura vs dosis): {'cloro-granulado': 100.0, 'clarificador': 100.0}
  Faltantes para aplicar hoy: {}
  Registro visita: OK → Estado agua 100.0%. Faltantes: {}
- Pileta P-MED (25000 L) de cliente 111
  Estado agua: 0.0%  |  acción: choque
  % productos en PILETA (estimado hoy): {'cloro-granulado': 0.0, 'clarificador': 0.0, 'alguicida': 0.0}
  % productos en CASA del cliente (cobertura vs dosis): {'cloro-granulado': 16.7, 'clarificador': 25.0, 'alguicida': 80.0}
  Faltantes para aplicar hoy: {'cloro-granulado': 250.0, 'clarificador': 150.0, 'alguicida': 12.5}
  Registro visita: DEBO IR → ...
...
SIMULACIÓN: preparo kit para la pileta P-MED (choque) del cliente 111
  Descuento local: cloro-granulado (sku=CL-GR-1) x 1 unidad | stock ahora=4.0
  Descuento local: clarificador (sku=CL-AR-3) x 1 unidad | stock ahora=4.0
  Descuento local: alguicida (sku=AL-GI-4) x 1 unidad | stock ahora=4.0

[OK] Resumen persistido en data/resumen_aquakeeper.dat
======================================================================
EJEMPLO COMPLETADO (AquaKeeper)
[OK] SINGLETON | [OK] FACTORY | [OK] OBSERVER | [OK] STRATEGY
======================================================================

🔧 Configuración (rápido)

Todo se ajusta en config/constantes.py:
-Litros típicos de piletas (chica/mediana/grande).
-Dosis base por 10.000 L (por tipo y estrategia).
-Umbrales: pH ideal, turbidez máxima, algas.
-Mínimos de stock (local / cliente).

🧭 Roadmap (ideas para crecer)

Persistencia SQLite/SQLAlchemy (clientes, piletas, productos, movimientos).
Promociones (Strategy de pricing): 2×1, membresías, marcas.
Agenda de visitas + recordatorios.
Reportes (faltantes por cliente, top productos, alertas próximas).
API (FastAPI) y panel web.
Integrar mediciones reales (CSV, sensores, app móvil).

✅ Checklist (rúbrica típica)
✅ 4 patrones implementados (Strategy/Factory/Observer/Singleton)
✅ Dominios claros (Cliente, Pileta, Producto, Stock, Visita)
✅ Dosis por estrategia y escalado por litros
✅ Cálculo de estado del agua (pH, turbidez, algas)
✅ Cobertura en casa del cliente vs dosis requerida
✅ Faltantes + decisión “DEBO IR”
✅ Control de stock del local con alertas
✅ Persistencia de resumen en data/

## ⚙️ Cómo ejecutar

### Opción A — directa
```bash
python3 src/main.py
