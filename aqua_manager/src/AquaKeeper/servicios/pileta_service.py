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
