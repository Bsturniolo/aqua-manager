"""
Archivo integrador generado automaticamente
Directorio: /home/bautista/aqua_manager/src/AquaKeeper/patrones/observer
Fecha: 2025-11-04 16:32:00
Total de archivos integrados: 1
"""

# ================================================================================
# ARCHIVO 1/1: observer.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/patrones/observer/observer.py
# ================================================================================

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


