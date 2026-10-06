from ..concurrencia.lock_visible import LockVisible


class Caja:
    """Caja registradora: dinero y marcador, protegidos con un LOCK."""

    def __init__(self, dinero_inicial, multa):
        self.lock = LockVisible()
        self.dinero = dinero_inicial
        self.entregados = 0
        self.perdidos = 0
        self.multa = multa
        self._resumen_previo = (0, 0, dinero_inicial)

    def cobrar(self, pedido, quien):
        """Cobra un pedido entregado. Devuelve (ganancia, a_tiempo)."""
        precio = pedido.receta.precio
        with self.lock.de(quien):
            a_tiempo = pedido.restante() >= 0
            ganancia = precio if a_tiempo else precio // 2
            self.dinero += ganancia
            self.entregados += 1
        return ganancia, a_tiempo

    def multar(self):
        """Cobra la multa de un pedido perdido. Devuelve el monto."""
        with self.lock.de("Caja"):
            self.dinero -= self.multa
            self.perdidos += 1
        return self.multa

    def pagar(self, monto, quien):
        """Descuenta `monto` si alcanza. Devuelve True si se pudo pagar."""
        with self.lock.de(quien):
            if self.dinero < monto:
                return False
            self.dinero -= monto
            return True

    def resumen_parcial(self):
        """(entregados, perdidos, ganancia) desde el último resumen."""
        e0, p0, d0 = self._resumen_previo
        with self.lock.de("Resumen"):
            datos = (self.entregados - e0, self.perdidos - p0, self.dinero - d0)
            self._resumen_previo = (self.entregados, self.perdidos, self.dinero)
        return datos
