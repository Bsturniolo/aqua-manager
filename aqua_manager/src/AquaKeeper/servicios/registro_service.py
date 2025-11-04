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
