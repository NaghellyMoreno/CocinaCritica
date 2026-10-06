from dataclasses import dataclass
from typing import Dict, List

from ..dominio.estacion import FotoEstacion
from ..dominio.pedido import Pedido


@dataclass(frozen=True)
class FotoBarrera:
    esperando: int
    partes: int


@dataclass(frozen=True)
class FotoJuego:
    """Todo lo que la interfaz necesita leer, en una sola copia de solo lectura."""
    servicio: int
    n_servicios: int
    abierto: bool
    cierre_activo: bool
    fin_servicio: float
    barrera_inicio: FotoBarrera
    barrera_fin: FotoBarrera
    dueno_despensa: object
    stock: Dict[str, int]
    violaciones_despensa: int
    dueno_caja: object
    dinero: int
    entregados: int
    perdidos: int
    estaciones: Dict[str, FotoEstacion]
    pedidos: List[Pedido]
    max_pedidos: int
    hilos_vivos: int

    @property
    def violaciones(self):
        return (sum(e.violaciones for e in self.estaciones.values())
                + self.violaciones_despensa)
