import itertools
import time

EN_ESPERA = "en espera"
PREPARANDO = "preparando"


class Pedido:
    _ids = itertools.count(1)

    def __init__(self, receta, espera, ahora=time.time):
        self.id = next(Pedido._ids)
        self.receta = receta
        self.espera = espera              # segundos que el cliente espera
        self._ahora = ahora
        self.limite = ahora() + espera
        self.estado = EN_ESPERA
        self.cocinero = None

    def restante(self):
        return self.limite - self._ahora()

    def asignar(self, cocinero):
        self.estado, self.cocinero = PREPARANDO, cocinero
