"""Dónde se dibuja cada cosa en el lienzo."""

from ..dominio.destinos import (DESPENSA, LAVAMANOS, MOSTRADOR, EnCola,
                                EnPuesto, EnSobrecupo, EnZona)

ANCHO, ALTO = 740, 720

ZONAS = {  # rectángulos (x0, y0, x1, y1)
    LAVAMANOS: (20, 20, 230, 160),
    DESPENSA: (255, 20, 485, 160),
    MOSTRADOR: (510, 20, 720, 160),
}

# esquina superior izquierda de cada estación en el lienzo
ORIGEN_ESTACIONES = {"Tablas": (20, 212), "Estufas": (380, 212), "Horno": (20, 487)}
PUESTO_W, PUESTO_H, PUESTO_GAP = 150, 110, 20
SINGULAR = {"Tablas": "Tabla", "Estufas": "Estufa", "Horno": "Horno"}

PEDIDOS_XY = (380, 487)        # esquina de la primera tarjeta de pedido


def puesto_rect(clave, i):
    x0, y0 = ORIGEN_ESTACIONES[clave]
    x = x0 + i * (PUESTO_W + PUESTO_GAP)
    return x, y0, x + PUESTO_W, y0 + PUESTO_H


def pies_en_puesto(clave, i):
    """Dónde se para el cocinero dentro de un puesto (los aparatos van a su derecha)."""
    x0, y0, x1, y1 = puesto_rect(clave, i)
    return x0 + 30, y1 - 20


class Posiciones:
    """Traduce el destino lógico de un cocinero a coordenadas del lienzo
    (el punto entre sus pies).

    Cada tipo de destino tiene su propia regla; para agregar uno nuevo basta
    con registrar su función en `_reglas`.
    """

    def __init__(self, cocineros):
        self._orden = {n: k for k, n in enumerate(cocineros)}
        self._reglas = {
            EnZona: self._en_zona,
            EnPuesto: self._en_puesto,
            EnSobrecupo: self._en_sobrecupo,
            EnCola: self._en_cola,
        }

    def xy(self, nombre, destino, foto):
        return self._reglas[type(destino)](nombre, destino, foto)

    def _en_zona(self, nombre, d, foto):
        x0, y0, x1, y1 = ZONAS[d.zona]
        return x0 + 45 + self._orden[nombre] * 60, y1 - 16

    def _en_puesto(self, nombre, d, foto):
        return pies_en_puesto(d.estacion, d.indice)

    def _en_sobrecupo(self, nombre, d, foto):
        x0, y0 = ORIGEN_ESTACIONES[d.estacion]
        nombres = [o.cocinero for o in foto.estaciones[d.estacion].sobrecupo]
        pos = nombres.index(nombre) if nombre in nombres else 0
        return x0 + 22 + pos * 40, y0 + PUESTO_H + 40

    def _en_cola(self, nombre, d, foto):
        x0, y0 = ORIGEN_ESTACIONES[d.estacion]
        esperando = foto.estaciones[d.estacion].esperando
        pos = esperando.index(nombre) if nombre in esperando else self._orden[nombre]
        return x0 + 26 + pos * 48, y0 + PUESTO_H + 98     # fila de espera
