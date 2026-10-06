import random

from ..dominio.pedido import Pedido


class GeneradorPedidos:
    """HILO que trae clientes nuevos mientras el servicio está abierto."""

    def __init__(self, tablero, control, recetas, tiempo_pedido, intervalo,
                 iniciales, notificador, elegir=random.choice):
        self._tablero = tablero
        self._control = control
        self._recetas = list(recetas)
        self._tiempo_pedido = tiempo_pedido
        self._intervalo = intervalo
        self._iniciales = iniciales
        self._avisos = notificador
        self._elegir = elegir

    def ejecutar(self):
        for _ in range(self._iniciales):       # arranque: un pedido por cocinero
            self.nuevo_pedido()
        # Event.wait(t) = pausa que se corta apenas cierra la cocina (Paso 14)
        while not self._control.esperar_cierre(random.uniform(*self._intervalo)):
            self.nuevo_pedido()

    def nuevo_pedido(self):
        p = self._tablero.agregar(
            lambda: Pedido(self._elegir(self._recetas), self._tiempo_pedido))
        if p is not None:
            self._avisos.log(f"Nuevo pedido: {p.receta.nombre} #{p.id}")
