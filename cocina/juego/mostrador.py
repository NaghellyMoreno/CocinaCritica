from ..eventos import ResumenServicio


class Mostrador:
    """Cierra cada pedido: lo cobra o lo multa, lo quita del tablero y avisa."""

    def __init__(self, caja, tablero, notificador):
        self._caja = caja
        self._tablero = tablero
        self._avisos = notificador

    def entregar(self, p, quien):
        ganancia, a_tiempo = self._caja.cobrar(p, quien)
        self._tablero.quitar(p)
        nota = "" if a_tiempo else " (tarde, mitad de precio)"
        self._avisos.log(f"{quien} entregó {p.receta.nombre} #{p.id}: +${ganancia}{nota}")

    def perder(self, p, motivo):
        multa = self._caja.multar()
        self._tablero.quitar(p)
        self._avisos.log(f"Perdido {p.receta.nombre} #{p.id}: {motivo} (-${multa})")

    def cerrar_servicio(self, numero):
        """Acción de la barrera de cierre: la ejecuta UN hilo cuando llegan todos."""
        for p in self._tablero.sacar_pendientes():
            self.perder(p, "quedó sin atender al cierre")
        entregados, perdidos, ganancia = self._caja.resumen_parcial()
        self._avisos.publicar(ResumenServicio(numero, entregados, perdidos, ganancia))
