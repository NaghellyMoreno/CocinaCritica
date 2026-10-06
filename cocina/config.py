"""Configuración del juego (puedes cambiar estos valores)."""

from dataclasses import dataclass, field
from typing import Dict, Tuple

from .dominio.receta import Receta

PRECIOS = {"Tomate": 1, "Cebolla": 1, "Carne": 3, "Pan": 1, "Masa": 2, "Queso": 2}


def _recetas():
    return {
        "Sopa": Receta(
            nombre="Sopa",
            ingredientes={"Tomate": 1, "Cebolla": 1},
            pasos=(("Tablas", 2.0), ("Estufas", 3.0)),
            precio=8,
        ),
        "Hamburguesa": Receta(
            nombre="Hamburguesa",
            ingredientes={"Carne": 1, "Pan": 1, "Cebolla": 1},
            pasos=(("Tablas", 1.5), ("Estufas", 3.5)),
            precio=14,
        ),
        "Pizza": Receta(
            nombre="Pizza",
            ingredientes={"Masa": 1, "Queso": 1, "Tomate": 1},
            pasos=(("Tablas", 1.5), ("Horno", 4.5)),
            precio=16,
        ),
    }


@dataclass(frozen=True)
class Configuracion:
    n_servicios: int = 3               # cuántas rondas tiene la jornada
    duracion_servicio: float = 60      # segundos que dura cada servicio
    tiempo_pedido: float = 35          # segundos que un cliente espera su plato
    max_pedidos: int = 6               # pedidos pendientes como máximo
    intervalo_pedidos: Tuple[float, float] = (2.5, 4.5)  # entre pedidos nuevos
    pausa_ingenua: float = 0.5         # "hueco" entre comprobar y actuar (modo inseguro)
    caminar: float = 0.45              # segundos que tarda un cocinero en desplazarse
    multa: int = 3                     # dinero que pierdes por pedido no entregado

    cocineros: Tuple[str, ...] = ("Ana", "Luis", "Sofi")

    precios: Dict[str, int] = field(default_factory=lambda: dict(PRECIOS))
    stock_inicial: Dict[str, int] = field(
        default_factory=lambda: {i: 4 for i in PRECIOS})
    dinero_inicial: int = 20
    unidades_compra: int = 3           # cuántas unidades trae cada compra

    recetas: Dict[str, Receta] = field(default_factory=_recetas)

    # (clave, nombre en pantalla, puestos)
    estaciones: Tuple[Tuple[str, str, int], ...] = (
        ("Tablas", "Tablas de picar", 2),
        ("Estufas", "Estufas", 2),
        ("Horno", "Horno", 1),
    )

    # tiempos menores de la simulación
    pausa_contar: float = 0.2          # contar y sacar ingredientes (con lock)
    pausa_reponer: float = 0.15        # guardar una compra en la despensa
    sondeo_ingenuo: float = 0.05       # cada cuánto mira si hay puesto (modo inseguro)
    lavado: Tuple[float, float] = (1.0, 3.0)   # lavarse las manos
    espera_pedido: float = 0.3         # cuánto espera un cocinero un pedido nuevo
    reintento_ingredientes: float = 0.6
