import threading

from ..eventos import FinJuego, PuedeAbrir


class Jefe:
    """HILO del jefe: abre y cierra cada servicio."""

    def __init__(self, control, generador, n_servicios, notificador):
        self._control = control
        self._generador = generador
        self._n_servicios = n_servicios
        self._avisos = notificador

    def ejecutar(self):
        c = self._control
        for s in range(1, self._n_servicios + 1):
            c.preparar(s)
            self._avisos.publicar(PuedeAbrir(s))
            c.esperar_orden_abrir()
            self._avisos.log(f"Jefe: abriendo servicio {s}, espero a los cocineros")
            c.esperar_inicio()                        # BARRERA de inicio
            threading.Thread(target=self._generador.ejecutar, name="Generador",
                             daemon=True).start()
            c.durar()
            c.cerrar()
            self._avisos.log("¡Cierre de cocina! Cada uno termina su plato")
            c.esperar_fin()                           # BARRERA de cierre
        self._avisos.publicar(FinJuego())
