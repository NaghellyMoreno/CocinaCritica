import time

from ..concurrencia.lock_visible import LockVisible


class Despensa:
    """Ingredientes compartidos, protegidos con un LOCK."""

    def __init__(self, stock_inicial, pausa_reponer=0.15):
        self.stock = dict(stock_inicial)
        self.lock = LockVisible()
        self.violaciones = 0
        self._pausa_reponer = pausa_reponer

    def hay(self, ingredientes):
        return all(self.stock[i] >= n for i, n in ingredientes.items())

    def descontar(self, ingredientes):
        """Resta sin protección propia: quien llama decide si usa el lock."""
        for i, n in ingredientes.items():
            self.stock[i] -= n
            if self.stock[i] < 0:
                self.violaciones += 1

    def tomar(self, ingredientes, quien, modo):
        """Saca los ingredientes según el `modo` de sincronización (Strategy)."""
        return modo.tomar_ingredientes(self, ingredientes, quien)

    def agregar(self, ingrediente, n, quien):
        with self.lock.de(quien):
            time.sleep(self._pausa_reponer)
            self.stock[ingrediente] += n

    def foto(self):
        # Sin lock a propósito: la interfaz no debe quedarse esperando a que
        # un cocinero termine de contar ingredientes.
        return dict(self.stock)
