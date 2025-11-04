"""
Archivo integrador generado automaticamente
Directorio: /home/bautista/aqua_manager/src/AquaKeeper/patrones/strategy
Fecha: 2025-11-04 16:32:00
Total de archivos integrados: 1
"""

# ================================================================================
# ARCHIVO 1/1: dosificacion.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/patrones/strategy/dosificacion.py
# ================================================================================

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


