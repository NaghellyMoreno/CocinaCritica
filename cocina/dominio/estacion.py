import threading
import time
from dataclasses import dataclass
from typing import List, Optional

from .destinos import EnPuesto, EnSobrecupo


@dataclass(eq=False)
class Ocupacion:
    """Lo que se dibuja en un puesto ocupado."""
    cocinero: str
    plato: str
    inicio: float
    duracion: float


@dataclass(frozen=True)
class FotoEstacion:
    """Copia del estado de una estación para dibujar (la usa la interfaz)."""
    clave: str
    etiqueta: str
    capacidad: int
    puestos: List[Optional[Ocupacion]]
    sobrecupo: List[Ocupacion]
    esperando: List[str]
    contador_semaforo: int
    violaciones: int

    @property
    def usados(self):
        return sum(p is not None for p in self.puestos) + len(self.sobrecupo)


class Lugar:
    """Dónde quedó un cocinero dentro de una estación."""

    def __init__(self, estacion, indice, token, sobrecupo, dato):
        self.estacion = estacion
        self.dato = dato              # lo que se dibuja en el puesto
        self.indice = indice          # número de puesto (o None si es sobrecupo)
        self.token = token            # True si de verdad adquirió el semáforo
        self.sobrecupo = sobrecupo

    @property
    def destino(self):
        if self.sobrecupo:
            return EnSobrecupo(self.estacion.clave)
        return EnPuesto(self.estacion.clave, self.indice)


class Estacion:
    """Estación de cocina con `capacidad` puestos, protegida con un SEMÁFORO."""

    def __init__(self, clave, etiqueta, capacidad, ahora=time.time):
        self.clave, self.etiqueta, self.capacidad = clave, etiqueta, capacidad
        self.semaforo = threading.BoundedSemaphore(capacidad)
        self.puestos = [None] * capacidad   # qué hay en cada puesto
        self.sobrecupo = []                 # solo se llena en modo inseguro
        self.esperando = []                 # cola visible
        self._datos = threading.Lock()      # protege las listas de arriba
        self.violaciones = 0
        self._ahora = ahora

    def ocupados(self):
        with self._datos:
            return sum(p is not None for p in self.puestos) + len(self.sobrecupo)

    def entrar(self, quien, plato, duracion, modo):
        """Espera un puesto según el `modo` de sincronización (Strategy)."""
        with self._datos:
            self.esperando.append(quien)

        token = modo.ocupar_puesto(self)

        dato = Ocupacion(quien, plato, self._ahora(), duracion)
        with self._datos:
            self.esperando.remove(quien)
            if None in self.puestos:
                i = self.puestos.index(None)
                self.puestos[i] = dato
                return Lugar(self, i, token, False, dato)
            self.sobrecupo.append(dato)      # ¡más cocineros que puestos!
            self.violaciones += 1
            return Lugar(self, None, token, True, dato)

    def salir(self, lugar):
        with self._datos:
            if lugar.sobrecupo:
                self.sobrecupo = [d for d in self.sobrecupo if d is not lugar.dato]
            else:
                self.puestos[lugar.indice] = None
        if lugar.token:
            self.semaforo.release()

    def contador_semaforo(self):
        # threading no expone el contador del semáforo; lo leemos (solo para
        # mostrarlo) en este único lugar para no regar el atributo privado.
        return self.semaforo._value

    def foto(self):
        with self._datos:
            return FotoEstacion(
                clave=self.clave, etiqueta=self.etiqueta, capacidad=self.capacidad,
                puestos=list(self.puestos), sobrecupo=list(self.sobrecupo),
                esperando=list(self.esperando),
                contador_semaforo=self.contador_semaforo(),
                violaciones=self.violaciones)
