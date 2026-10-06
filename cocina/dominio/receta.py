from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Receta:
    nombre: str
    ingredientes: Dict[str, int]
    pasos: Tuple[Tuple[str, float], ...]   # (clave de estación, segundos)
    precio: int
