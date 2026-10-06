import threading

from ..concurrencia.control_servicio import ControlServicio
from ..concurrencia.sincronizacion import (SelectorSincronizacion,
                                           SincronizacionIngenua,
                                           SincronizacionSegura)
from ..config import Configuracion
from ..dominio.caja import Caja
from ..dominio.despensa import Despensa
from ..dominio.estacion import Estacion
from ..dominio.tablero import Tablero
from ..eventos import ColaEventos
from .cocinero import Cocinero
from .compras import Compras
from .foto import FotoBarrera, FotoJuego
from .generador import GeneradorPedidos
from .jefe import Jefe
from .mostrador import Mostrador


class Juego:
    """Arma todas las piezas y le ofrece a la interfaz una fachada pequeña.

    La interfaz solo usa: iniciar, abrir_servicio, comprar, usar_sincronizacion,
    eventos_pendientes, foto, cocineros, unidades_compra y opciones_compra.
    """

    def __init__(self, conf=None, eventos=None):
        conf = conf or Configuracion()
        self.conf = conf
        self._eventos = eventos or ColaEventos()

        self._sync = SelectorSincronizacion(
            SincronizacionSegura(conf.pausa_contar),
            SincronizacionIngenua(conf.pausa_ingenua, conf.sondeo_ingenuo))
        self._estaciones = {c: Estacion(c, e, n) for c, e, n in conf.estaciones}
        self._despensa = Despensa(conf.stock_inicial, conf.pausa_reponer)
        self._caja = Caja(conf.dinero_inicial, conf.multa)
        self._tablero = Tablero(conf.max_pedidos)
        self._mostrador = Mostrador(self._caja, self._tablero, self._eventos)
        self._compras = Compras(self._caja, self._despensa, conf.precios,
                                conf.unidades_compra, self._eventos)

        partes = len(conf.cocineros) + 1              # cocineros + jefe
        self._control = ControlServicio(partes, conf.duracion_servicio,
                                        self._al_abrir,
                                        self._mostrador.cerrar_servicio)
        generador = GeneradorPedidos(
            self._tablero, self._control, conf.recetas.values(),
            conf.tiempo_pedido, conf.intervalo_pedidos, len(conf.cocineros),
            self._eventos)
        self._jefe = Jefe(self._control, generador, conf.n_servicios, self._eventos)
        self._cocineros = [
            Cocinero(nombre, self._control, self._tablero, self._despensa,
                     self._estaciones, self._mostrador, self._sync,
                     self._eventos, conf)
            for nombre in conf.cocineros]

    def _al_abrir(self, numero):
        self._eventos.log(f"--- Servicio {numero} abierto ---")

    # --- fachada para la interfaz --------------------------------------------
    @property
    def cocineros(self):
        return tuple(self.conf.cocineros)

    @property
    def unidades_compra(self):
        return self._compras.unidades

    def opciones_compra(self):
        return self._compras.opciones()

    def iniciar(self):
        for c in self._cocineros:
            threading.Thread(target=c.ejecutar, name=c.nombre, daemon=True).start()
        threading.Thread(target=self._jefe.ejecutar, name="Jefe", daemon=True).start()

    def abrir_servicio(self):
        self._control.dar_orden_abrir()

    def comprar(self, ingrediente):
        """La compra corre en un hilo aparte para no congelar la interfaz."""
        threading.Thread(target=self._compras.comprar, args=(ingrediente,),
                         name="Compra", daemon=True).start()

    def usar_sincronizacion(self, seguro):
        modo = self._sync.usar(seguro)
        self._eventos.log(f"*** Modo {modo.nombre} activado ***")

    def eventos_pendientes(self):
        return self._eventos.pendientes()

    def foto(self):
        c, caja, despensa = self._control, self._caja, self._despensa
        bi, bf = c.barrera_inicio, c.barrera_fin
        return FotoJuego(
            servicio=c.numero,
            n_servicios=self.conf.n_servicios,
            abierto=c.esta_abierto(),
            cierre_activo=c.cierre_activo(),
            fin_servicio=c.fin,
            barrera_inicio=FotoBarrera(bi.n_waiting, bi.parties),
            barrera_fin=FotoBarrera(bf.n_waiting, bf.parties),
            dueno_despensa=despensa.lock.dueno,
            stock=despensa.foto(),
            violaciones_despensa=despensa.violaciones,
            # El dinero y el marcador se leen sin lock, igual que antes: la
            # interfaz no debe bloquearse esperando la caja.
            dueno_caja=caja.lock.dueno,
            dinero=caja.dinero,
            entregados=caja.entregados,
            perdidos=caja.perdidos,
            estaciones={k: e.foto() for k, e in self._estaciones.items()},
            pedidos=self._tablero.visibles(),
            max_pedidos=self._tablero.max_pedidos,
            hilos_vivos=threading.active_count(),
        )
