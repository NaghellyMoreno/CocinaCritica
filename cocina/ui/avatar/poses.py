"""
Animaciones de los avatares, como POSES calculadas a partir del tiempo.

Una pose dice dónde van los pies y las manos, qué cara pone el cocinero, qué
tiene en la mano y qué efectos lo rodean. Son funciones puras (sin Tkinter):
el dibujo está en dibujo.py.

Coordenadas relativas a los pies del avatar: x hacia la derecha, y hacia
abajo (así que "arriba" es negativo). Escala 1 = tamaño en el juego.
"""

import math
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from ...dominio.actividad import Actividad

MANO_IZQ = (-14.0, -16.0)
MANO_DER = (14.0, -16.0)


@dataclass(frozen=True)
class Pose:
    rebote: float = 0.0                       # sube/baja el torso (negativo = arriba)
    pie_izq: Tuple[float, float] = (-5.0, 0.0)    # (x, altura levantado)
    pie_der: Tuple[float, float] = (5.0, 0.0)
    mano_izq: Tuple[float, float] = MANO_IZQ
    mano_der: Tuple[float, float] = MANO_DER
    cara: str = "normal"                      # ver dibujo.CARAS
    mirada: float = 0.0                       # -1 izquierda … 1 derecha
    objeto: Optional[str] = None              # ver dibujo.OBJETOS
    efectos: Tuple[str, ...] = ()             # ver dibujo.EFECTOS


def _respirar(t):
    return math.sin(t * 2) * 0.6


# --- una función por actividad -----------------------------------------------
def reposo(t, estacion):
    return Pose(rebote=_respirar(t))


def libre(t, estacion):
    return Pose(rebote=_respirar(t), mirada=math.sin(t * 1.3))


def lavar(t, estacion):
    a = math.sin(t * 14) * 3
    b = math.sin(t * 7) * 2
    return Pose(rebote=_respirar(t), mano_izq=(-4 + a, -19 + b),
                mano_der=(4 - a, -19 - b), efectos=("burbujas",))


def barrera(t, estacion):
    bostezando = t % 5 < 1.3
    if bostezando:
        return Pose(rebote=-1.0, mano_der=(4, -36), cara="bostezo")
    return Pose(rebote=math.sin(t * 1.2) * 0.8, cara="aburrido", efectos=("zzz",))


def buscar(t, estacion):
    a = math.sin(t * 6)
    return Pose(rebote=_respirar(t), mano_izq=(-12, -30 - max(0, a) * 10),
                mano_der=(12, -30 - max(0, -a) * 10), cara="concentrado")


def sin_ingredientes(t, estacion):
    return Pose(rebote=math.sin(t * 20) * 0.8, mano_izq=(-12, -42),
                mano_der=(12, -42), cara="preocupado",
                efectos=("sudor", "alerta"))


def en_cola(t, estacion):
    return Pose(rebote=_respirar(t), pie_der=(5, max(0.0, math.sin(t * 9)) * 3),
                mano_izq=(6, -24), mano_der=(-6, -23), cara="impaciente",
                mirada=math.sin(t * 0.8))


def entregar(t, estacion):
    return Pose(rebote=-abs(math.sin(t * 5)) * 1.5, mano_izq=(-8, -24),
                mano_der=(8, -24), cara="feliz", objeto="plato",
                efectos=("estrellas",))


def fin(t, estacion):
    return Pose(rebote=_respirar(t), mano_der=(17, -40 + math.sin(t * 8) * 4),
                cara="feliz")


# --- cocinar: una acción por estación -----------------------------------------
def picar(t):
    k = abs(math.sin(t * 10))
    return Pose(mano_der=(18, -22 - k * 9), mano_izq=(9, -18), cara="concentrado",
                mirada=1, objeto="cuchillo", efectos=("picados",))


def revolver(t):
    return Pose(mano_der=(22 + math.cos(t * 6) * 4, -36 + math.sin(t * 6) * 2),
                cara="concentrado", mirada=1, objeto="cuchara",
                efectos=("vapor",))


def hornear(t):
    d = (math.sin(t * 2.5) + 1) / 2 * 6
    return Pose(mano_der=(16 + d, -21), mano_izq=(10 + d, -20), cara="concentrado",
                mirada=1, objeto="pala", efectos=("calor",))


ACCIONES_ESTACION = {"Tablas": picar, "Estufas": revolver, "Horno": hornear}


def cocinar(t, estacion):
    return ACCIONES_ESTACION.get(estacion, revolver)(t)


POSES = {
    Actividad.LAVANDO: lavar,
    Actividad.BARRERA: barrera,
    Actividad.LIBRE: libre,
    Actividad.BUSCANDO: buscar,
    Actividad.SIN_INGREDIENTES: sin_ingredientes,
    Actividad.EN_COLA: en_cola,
    Actividad.COCINANDO: cocinar,
    Actividad.ENTREGANDO: entregar,
    Actividad.FIN: fin,
}


def caminar(t, direccion):
    s = math.sin(t * 12)
    return Pose(rebote=-abs(s) * 2.5,
                pie_izq=(-5 + s * 4, max(0.0, s) * 2),
                pie_der=(5 - s * 4, max(0.0, -s) * 2),
                mano_izq=(-14, -17 - s * 3), mano_der=(14, -17 + s * 3),
                mirada=direccion)


def pose_para(actividad, estacion, t, caminando=False, direccion=0.0, feliz=False):
    """La pose de un cocinero en el instante `t`.

    Caminando manda sobre la actividad; `feliz` (recién entregó un plato)
    le pone una sonrisa a cualquier pose.
    """
    if caminando:
        pose = caminar(t, direccion)
    else:
        pose = POSES.get(actividad, reposo)(t, estacion)
    if feliz and pose.cara in ("normal", "concentrado", "impaciente", "aburrido"):
        pose = replace(pose, cara="feliz")
    return pose
