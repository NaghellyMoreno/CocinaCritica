import queue
import threading


class Tablero:
    """Pedidos visibles (lista con lock) y pendientes de preparar (queue.Queue)."""

    def __init__(self, max_pedidos):
        self.max_pedidos = max_pedidos
        self._visibles = []
        self._lock = threading.Lock()
        self._pendientes = queue.Queue()

    def agregar(self, crear_pedido):
        """Crea y publica un pedido si hay lugar; si no, devuelve None.

        Recibe una fábrica para que comprobar el cupo y crear el pedido sean
        una sola operación (y no se gasten números de pedido de más).
        """
        with self._lock:
            if len(self._visibles) >= self.max_pedidos:
                return None
            p = crear_pedido()
            self._visibles.append(p)
        self._pendientes.put(p)
        return p

    def siguiente(self, timeout):
        """El próximo pedido por preparar, o None si no llegó ninguno a tiempo."""
        try:
            return self._pendientes.get(timeout=timeout)
        except queue.Empty:
            return None

    def sacar_pendientes(self):
        """Saca, uno por uno, los pedidos que nadie tomó."""
        while True:
            try:
                p = self._pendientes.get_nowait()
            except queue.Empty:
                return
            yield p

    def quitar(self, p):
        with self._lock:
            if p in self._visibles:
                self._visibles.remove(p)

    def visibles(self):
        with self._lock:
            return list(self._visibles)
