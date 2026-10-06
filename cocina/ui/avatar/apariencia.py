"""Cómo se ve cada cocinero y qué opciones hay para elegir."""

import random
from dataclasses import dataclass

PIELES = ("#ffdbac", "#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#5c3a1e")
COLORES_PELO = ("#2c1b10", "#5a3825", "#a0522d", "#e6c35c", "#b8b8b8", "#c0392b")
# El delantal también es "el color del cocinero" en paneles y puestos, así que
# son colores que se leen bien sobre el fondo crema.
DELANTALES = ("#e4572e", "#2e86ab", "#7a5cc2", "#2a9d8f",
              "#d1495b", "#00798c", "#c06c84", "#8d6346")
PEINADOS = ("Corto", "Largo", "Cola", "Rizado", "Calvo")
ACCESORIOS = ("Gorro de chef", "Pañuelo", "Lentes", "Bigote", "Ninguno")


@dataclass(frozen=True)
class Apariencia:
    piel: str
    peinado: str
    pelo: str
    delantal: str
    accesorio: str


def apariencia_inicial(k):
    """Diseño por defecto del k-ésimo cocinero (los colores de siempre)."""
    base = (
        Apariencia(PIELES[0], "Cola", COLORES_PELO[1], DELANTALES[0], "Gorro de chef"),
        Apariencia(PIELES[2], "Corto", COLORES_PELO[0], DELANTALES[1], "Bigote"),
        Apariencia(PIELES[3], "Rizado", COLORES_PELO[0], DELANTALES[2], "Lentes"),
    )
    if k < len(base):
        return base[k]
    return Apariencia(PIELES[k % len(PIELES)], PEINADOS[k % len(PEINADOS)],
                      COLORES_PELO[k % len(COLORES_PELO)],
                      DELANTALES[k % len(DELANTALES)], "Gorro de chef")


def apariencia_aleatoria(rng=random):
    return Apariencia(rng.choice(PIELES), rng.choice(PEINADOS),
                      rng.choice(COLORES_PELO), rng.choice(DELANTALES),
                      rng.choice(ACCESORIOS))
