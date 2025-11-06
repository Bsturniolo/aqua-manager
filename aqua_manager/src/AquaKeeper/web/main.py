
from fastapi import FastAPI
from pydantic import BaseModel
import io
from contextlib import redirect_stdout

# importa tu demo real
from AquaKeeper.demo import demo

# ← ESTA variable debe llamarse app (Uvicorn la busca así)
app = FastAPI(
    title="AquaKeeper Web",
    description="Wrapper web (FastAPI) para ejecutar la demo de AquaKeeper",
    version="1.0.0",
)

class RunResponse(BaseModel):
    ok: bool
    text: str

@app.get("/", summary="Ping")
def root():
    return {"ok": True, "service": "AquaKeeper on Render", "docs": "/docs"}

@app.post("/run", response_model=RunResponse, summary="Ejecutar demo() y capturar salida")
def run_demo():
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            demo()
        return RunResponse(ok=True, text=buf.getvalue())
    except Exception as e:
        return RunResponse(ok=False, text=f"ERROR: {e!r}")

import re
from typing import Any, Dict, List

def _parse_demo_text(txt: str) -> Dict[str, Any]:
    """
    Parser light para el texto actual de demo(): extrae productos y piletas.
    No toca tu lógica, solo busca patrones habituales en la impresión.
    """
    productos: List[Dict[str, str]] = []
    piletas: List[Dict[str, Any]] = []
    resumen: str | None = None

    # Productos: líneas que empiezan con "Producto:"
    # Ej: "Producto: Cloro Granulado Premium [cloro-granulado] (1kg)"
    re_prod = re.compile(r"^Producto:\s*(.+?)\s*\[(.+?)\]\s*\((.+?)\)\s*$")

    # Piletas: línea que empieza con "- Pileta"
    # Ej: "- Pileta P-CHICA (12000 L) de cliente 111"
    re_pileta = re.compile(r"^- Pileta\s+(.+?)\s+\((\d+)\s*L\)\s+de cliente\s+(\d+)", re.IGNORECASE)

    # Estado y acción
    # Ej: "  Estado agua: 100.0%  |  acción: mantenimiento"
    re_estado = re.compile(r"Estado agua:\s*([\d.]+)%\s*\|\s*acción:\s*(\w+)", re.IGNORECASE)

    # % productos en CASA del cliente (resumen)
    re_casa = re.compile(r"% productos en CASA.+:\s*\{(.+)\}")

    # Faltantes para aplicar hoy
    re_falt = re.compile(r"Faltantes.*:\s*\{(.*)\}")

    # Resumen final
    re_ok = re.compile(r"EJEMPLO COMPLETADO.*", re.IGNORECASE)

    current: Dict[str, Any] | None = None

    for raw in txt.splitlines():
        line = raw.strip()

        # productos
        m = re_prod.match(line)
        if m:
            productos.append({
                "nombre": m.group(1),
                "sku": m.group(2),
                "presentacion": m.group(3),
            })
            continue

        # comienzo de bloque pileta
        m = re_pileta.match(line)
        if m:
            if current:
                piletas.append(current)
            current = {
                "nombre": m.group(1),
                "litros": int(m.group(2)),
                "cliente_id": m.group(3),
            }
            continue

        # estado/accion
        m = re_estado.search(line)
        if m and current is not None:
            current["estado_agua_pct"] = float(m.group(1))
            current["accion"] = m.group(2)
            continue

        # productos en casa (coverage)
        m = re_casa.search(line)
        if m and current is not None:
            # parseo simple de dict estilo "{'cloro-granulado': 100.0, ...}"
            casa_txt = m.group(1)
            casa = {}
            for kv in casa_txt.split(","):
                if ":" in kv:
                    k, v = kv.split(":", 1)
                    casa[k.strip(" '\"")] = float(v.strip(" %"))
            current["stock_cliente_pct"] = casa
            continue

        # faltantes
        m = re_falt.search(line)
        if m and current is not None:
            falt_txt = m.group(1)
            faltantes = {}
            if falt_txt:
                for kv in falt_txt.split(","):
                    if ":" in kv:
                        k, v = kv.split(":", 1)
                        try:
                            faltantes[k.strip(" '\"")] = float(v)
                        except:
                            pass
            current["faltantes_hoy"] = faltantes
            continue

        # resumen OK
        if re_ok.search(line):
            resumen = line

    if current:
        piletas.append(current)

    return {
        "productos": productos,
        "piletas": piletas,
        "resumen": resumen,
    }

@app.post("/run-structured", summary="Ejecutar demo() y devolver JSON estructurado")
def run_structured():
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo()
    txt = buf.getvalue()
    data = _parse_demo_text(txt)
    return {"ok": True, "data": data, "raw_len": len(txt)}
