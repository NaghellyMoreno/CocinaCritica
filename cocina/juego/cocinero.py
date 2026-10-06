import random
import time

from ..dominio.actividad import Actividad
from ..dominio.destinos import DESPENSA, LAVAMANOS, MOSTRADOR, EnCola, EnZona
from ..eventos import EstadoCocinero, Movimiento


class Cocinero:
    """HILO cocinero: se lava, cruza la barrera y prepara pedidos solo."""

    def __init__(self, nombre, control, tablero, despensa, estaciones, mostrador,
                 sincronizacion, notificador, conf):
        self.nombre = nombre
        self._control = control
        self._tablero = tablero
        self._despensa = despensa
        self._estaciones = estaciones
        self._mostrador = mostrador
        self._sync = sincronizacion           # se lee en cada acceso: la UI lo cambia
        self._avisos = notificador
        self._conf = conf

    # --- comunicación con la interfaz (nunca tocamos Tkinter desde un hilo) --
    def _mover(self, destino):
        self._avisos.publicar(Movimiento(self.nombre, destino))
        time.sleep(self._conf.caminar)

    def _estado(self, texto, actividad, estacion=None):
        self._avisos.publicar(EstadoCocinero(self.nombre, texto, actividad, estacion))

    # --- el hilo -------------------------------------------------------------
    def ejecutar(self):
        c = self._control
        for _ in range(self._conf.n_servicios):
            self._mover(EnZona(LAVAMANOS))
            self._estado("Lavándose las manos", Actividad.LAVANDO)
            time.sleep(random.uniform(*self._conf.lavado))
            self._estado("Listo: esperando en la barrera", Actividad.BARRERA)
            c.esperar_inicio()                        # BARRERA de inicio
            while c.esta_abierto():
                p = self._tablero.siguiente(timeout=self._conf.espera_pedido)
                if p is None:
                    self._estado("Libre: esperando pedidos", Actividad.LIBRE)
                    continue
                if p.restante() <= 0:
                    self._mostrador.perder(p, "el cliente se fue")
                    continue
                self.preparar(p)
            self._mover(EnZona(LAVAMANOS))
            self._estado("Terminó: espera a los demás", Actividad.BARRERA)
            c.esperar_fin()                           # BARRERA de cierre
        self._estado("Fin de la jornada", Actividad.FIN)

    def preparar(self, p):
        receta = p.receta
        p.asignar(self.nombre)
        self._mover(EnZona(DESPENSA))
        self._estado(f"Busca ingredientes para {receta.nombre}", Actividad.BUSCANDO)
        while not self._despensa.tomar(receta.ingredientes, self.nombre,
                                       self._sync.actual):
            if not self._control.esta_abierto() or p.restante() <= 0:
                self._mostrador.perder(p, "no hubo ingredientes")
                return
            self._estado(f"¡Faltan ingredientes para {receta.nombre}!",
                         Actividad.SIN_INGREDIENTES)
            time.sleep(self._conf.reintento_ingredientes)

        for clave, duracion in receta.pasos:
            est = self._estaciones[clave]
            self._mover(EnCola(clave))
            self._estado(f"En cola: {est.etiqueta}", Actividad.EN_COLA, clave)
            lugar = est.entrar(self.nombre, receta.nombre, duracion, self._sync.actual)
            self._mover(lugar.destino)
            self._estado(f"{receta.nombre} en {est.etiqueta}", Actividad.COCINANDO, clave)
            time.sleep(duracion)
            est.salir(lugar)

        self._mover(EnZona(MOSTRADOR))
        self._mostrador.entregar(p, self.nombre)
        self._estado(f"Entregó {receta.nombre} #{p.id}", Actividad.ENTREGANDO)
