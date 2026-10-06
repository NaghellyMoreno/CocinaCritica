JEFE = "Jefe (tú)"


class Compras:
    """El jefe compra ingredientes: paga en la caja y repone la despensa."""

    def __init__(self, caja, despensa, precios, unidades, notificador):
        self._caja = caja
        self._despensa = despensa
        self._precios = precios
        self.unidades = unidades
        self._avisos = notificador

    def costo(self, ingrediente):
        return self._precios[ingrediente] * self.unidades

    def opciones(self):
        """(ingrediente, costo) de cada compra posible, para los botones."""
        return [(i, self.costo(i)) for i in self._precios]

    def comprar(self, ingrediente):
        costo = self.costo(ingrediente)
        if not self._caja.pagar(costo, JEFE):
            self._avisos.log(f"No alcanza el dinero para {self.unidades} de "
                             f"{ingrediente} (${costo})")
            return
        # Los dos locks NUNCA se anidan: así no hay riesgo de deadlock
        self._despensa.agregar(ingrediente, self.unidades, JEFE)
        self._avisos.log(f"Compraste {self.unidades} de {ingrediente} (-${costo})")
