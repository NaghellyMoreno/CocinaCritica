"""
Dónde está un cocinero, en términos lógicos (no en píxeles).

La interfaz traduce cada tipo de destino a coordenadas en el lienzo.
"""

from dataclasses import dataclass

LAVAMANOS = "Lavamanos"
DESPENSA = "Despensa"
MOSTRADOR = "Mostrador"


@dataclass(frozen=True)
class EnZona:
    zona: str


@dataclass(frozen=True)
class EnCola:
    estacion: str


@dataclass(frozen=True)
class EnPuesto:
    estacion: str
    indice: int


@dataclass(frozen=True)
class EnSobrecupo:
    estacion: str
