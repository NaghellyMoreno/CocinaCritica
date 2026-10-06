"""
Estrategias de sincronización (patrón Strategy).

Las estaciones y la despensa no saben si el juego está en modo seguro o no:
le piden a la estrategia activa que haga el acceso. Aquí quedan, lado a lado,
la versión CORRECTA y la INGENUA de cada acceso.
"""

import time
from abc import ABC, abstractmethod


class ModoSincronizacion(ABC):
    """Cómo acceden los cocineros a los recursos compartidos."""

    nombre = ""

    @abstractmethod
    def ocupar_puesto(self, estacion):
        """Espera un puesto en `estacion`. Devuelve True si adquirió el semáforo
        (y por lo tanto hay que liberarlo al salir)."""

    @abstractmethod
    def tomar_ingredientes(self, despensa, ingredientes, quien):
        """Intenta sacar `ingredientes`. Devuelve True si los tomó."""


class SincronizacionSegura(ModoSincronizacion):
    nombre = "seguro"

    def __init__(self, pausa_contar=0.2):
        self.pausa_contar = pausa_contar

    def ocupar_puesto(self, estacion):
        # CORRECTO: el semáforo garantiza que nunca entren más de `capacidad`
        estacion.semaforo.acquire()
        return True

    def tomar_ingredientes(self, despensa, ingredientes, quien):
        # CORRECTO: comprobar y descontar dentro del mismo lock
        with despensa.lock.de(quien):
            if not despensa.hay(ingredientes):
                return False
            time.sleep(self.pausa_contar)    # contar y sacar los ingredientes
            despensa.descontar(ingredientes)
            return True


class SincronizacionIngenua(ModoSincronizacion):
    """Sin semáforos ni locks: rompe los invariantes A PROPÓSITO, para verlo."""

    nombre = "SIN sincronización"

    def __init__(self, pausa=0.5, sondeo=0.05):
        self.pausa = pausa
        self.sondeo = sondeo

    def ocupar_puesto(self, estacion):
        # INGENUO: comprobar y luego actuar, sin protección (check-then-act)
        while estacion.ocupados() >= estacion.capacidad:
            time.sleep(self.sondeo)
        time.sleep(self.pausa)               # camina hacia el puesto "libre"...
        return False                         # ...que otro pudo ocupar mientras tanto

    def tomar_ingredientes(self, despensa, ingredientes, quien):
        # INGENUO: dos cocineros pueden ver el mismo último tomate
        if not despensa.hay(ingredientes):
            return False
        time.sleep(self.pausa)
        despensa.descontar(ingredientes)
        return True


class SelectorSincronizacion:
    """Guarda el modo activo: la interfaz lo cambia y los cocineros lo leen."""

    def __init__(self, segura, ingenua):
        self._segura, self._ingenua = segura, ingenua
        self.actual = segura

    def usar(self, seguro):
        self.actual = self._segura if seguro else self._ingenua
        return self.actual
