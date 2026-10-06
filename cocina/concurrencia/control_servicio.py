import threading
import time


class ControlServicio:
    """BARRERAS y Events que marcan el ritmo de cada servicio.

    `al_abrir(numero)` y `al_cerrar(numero)` son las acciones de las barreras:
    las ejecuta UN hilo cuando llegan todos, antes de liberar a los demás.
    """

    def __init__(self, partes, duracion, al_abrir, al_cerrar, ahora=time.time):
        self.duracion = duracion
        self._al_abrir, self._al_cerrar = al_abrir, al_cerrar
        self._ahora = ahora
        # La acción de la barrera corre ANTES de liberar a los hilos: así nadie
        # puede ver el servicio "cerrado" justo después de cruzar la barrera.
        self.barrera_inicio = threading.Barrier(partes, action=self._abrir)
        self.barrera_fin = threading.Barrier(partes, action=self._cerrar)
        self._abierto = threading.Event()          # servicio en curso
        self._cierre = threading.Event()           # para pausas interrumpibles
        self._orden_abrir = threading.Event()      # botón "Abrir servicio"
        self.numero = 0
        self.fin = 0.0

    # --- lo usa el jefe --------------------------------------------------------
    def preparar(self, numero):
        self.numero = numero

    def esperar_orden_abrir(self):
        self._orden_abrir.wait()                   # espera tu clic
        self._orden_abrir.clear()

    def durar(self):
        self._cierre.wait(self.duracion)           # dura el servicio

    def cerrar(self):
        self._abierto.clear()
        self._cierre.set()

    # --- lo usa la interfaz ----------------------------------------------------
    def dar_orden_abrir(self):
        self._orden_abrir.set()

    # --- lo usan todos los hilos -----------------------------------------------
    def esperar_inicio(self):
        self.barrera_inicio.wait()                 # BARRERA de inicio

    def esperar_fin(self):
        self.barrera_fin.wait()                    # BARRERA de cierre

    def esperar_cierre(self, timeout):
        """Pausa que se corta apenas cierra la cocina. True si ya cerró."""
        return self._cierre.wait(timeout)

    def esta_abierto(self):
        return self._abierto.is_set()

    def cierre_activo(self):
        return self._cierre.is_set()

    # --- acciones de las barreras ----------------------------------------------
    def _abrir(self):
        self._cierre.clear()
        self.fin = self._ahora() + self.duracion
        self._abierto.set()
        self._al_abrir(self.numero)

    def _cerrar(self):
        self._al_cerrar(self.numero)
