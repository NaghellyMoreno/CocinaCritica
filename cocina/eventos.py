"""
Mensajes de los hilos hacia la interfaz.

Los hilos nunca tocan Tkinter: publican eventos en una queue.Queue y el hilo
principal los lee. Cada tipo de mensaje es una clase, así agregar uno nuevo no
obliga a modificar el ciclo que los reparte.
"""

import queue
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Log:
    texto: str


@dataclass(frozen=True)
class Movimiento:
    cocinero: str
    destino: Any        # uno de los destinos de cocina.dominio.destinos


@dataclass(frozen=True)
class EstadoCocinero:
    cocinero: str
    texto: str
    actividad: Any = None   # cocina.dominio.actividad.Actividad
    estacion: Any = None    # clave de la estación, si aplica


@dataclass(frozen=True)
class PuedeAbrir:
    servicio: int


@dataclass(frozen=True)
class ResumenServicio:
    servicio: int
    entregados: int
    perdidos: int
    ganancia: int


@dataclass(frozen=True)
class FinJuego:
    pass


class Notificador(ABC):
    """Lo único que el juego necesita saber de quien lo observa."""

    @abstractmethod
    def publicar(self, evento):
        ...

    def log(self, texto):
        self.publicar(Log(texto))


class ColaEventos(Notificador):
    """Notificador respaldado por una queue.Queue (segura entre hilos)."""

    def __init__(self):
        self._cola = queue.Queue()

    def publicar(self, evento):
        self._cola.put(evento)

    def pendientes(self):
        """Saca todos los eventos acumulados sin bloquear (lo usa la interfaz)."""
        while True:
            try:
                evento = self._cola.get_nowait()
            except queue.Empty:
                return
            yield evento
