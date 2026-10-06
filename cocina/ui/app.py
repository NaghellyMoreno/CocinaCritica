from tkinter import messagebox

from ..eventos import (EstadoCocinero, FinJuego, Log, Movimiento, PuedeAbrir,
                       ResumenServicio)
from .panel import PanelControl
from .tema import FONDO
from .vista_cocina import VistaCocina


class App:
    """Une el juego con sus dos vistas y reparte los eventos de los hilos."""

    def __init__(self, root, juego, apariencias):
        self.root = root
        self.juego = juego
        root.title("Cocina concurrente — hilos, locks, semáforos y barreras")
        root.configure(bg=FONDO)

        # el delantal de cada cocinero es también su color en el panel
        colores = {n: apariencias[n].delantal for n in juego.cocineros}
        self.vista = VistaCocina(root, juego.cocineros, apariencias,
                                 juego.foto().estaciones)
        self.vista.grid(row=0, column=0, padx=8, pady=8, sticky="n")
        self.panel = PanelControl(root, juego.cocineros, colores,
                                  juego.opciones_compra(), juego.unidades_compra,
                                  al_abrir=juego.abrir_servicio,
                                  al_cambiar_modo=juego.usar_sincronizacion,
                                  al_comprar=juego.comprar)
        self.panel.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="n")

        # un manejador por tipo de evento: agregar uno no toca `_tick`
        self._manejadores = {
            Log: lambda e: self.panel.escribir(e.texto),
            Movimiento: lambda e: self.vista.mover(e.cocinero, e.destino),
            EstadoCocinero: self._estado_cocinero,
            PuedeAbrir: lambda e: self.panel.habilitar_abrir(e.servicio),
            ResumenServicio: self._resumen,
            FinJuego: lambda e: self.root.after(500, self._fin),
        }

        juego.iniciar()
        self._tick()

    # ---------- ciclo de la interfaz ----------
    def _tick(self):
        # 1) leer los mensajes que dejaron los hilos
        for evento in self.juego.eventos_pendientes():
            self._manejadores[type(evento)](evento)
        # 2) animar a los cocineros y 3) redibujar lo que cambia
        foto = self.juego.foto()
        self.vista.actualizar(foto)
        self.panel.actualizar(foto)
        self.root.after(40, self._tick)

    def _estado_cocinero(self, e):
        self.panel.estado_cocinero(e.cocinero, e.texto)
        self.vista.cambiar_actividad(e.cocinero, e.actividad, e.estacion)

    def _resumen(self, e):
        signo = "+" if e.ganancia >= 0 else "-"
        texto = (f"Servicio {e.servicio}: {e.entregados} entregados, "
                 f"{e.perdidos} perdidos, {signo}${abs(e.ganancia)}")
        self.panel.escribir("=== " + texto + " ===")
        self.vista.mostrar_banner(texto, 4)

    def _fin(self):
        foto = self.juego.foto()
        messagebox.showinfo(
            "Fin de la jornada",
            f"Dinero final: ${foto.dinero}\nEntregados: {foto.entregados}\n"
            f"Perdidos: {foto.perdidos}\nViolaciones de concurrencia: {foto.violaciones}")
