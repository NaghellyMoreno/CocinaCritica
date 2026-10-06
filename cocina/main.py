import tkinter as tk
from dataclasses import replace

from .config import Configuracion
from .juego.juego import Juego
from .ui.app import App
from .ui.pantalla_inicio import PantallaInicio
from .ui.tema import FONDO, configurar_estilos


def main():
    root = tk.Tk()
    root.title("Cocina concurrente — hilos, locks, semáforos y barreras")
    root.configure(bg=FONDO)
    configurar_estilos()
    conf = Configuracion()

    def empezar(perfiles):
        nombres = tuple(nombre for nombre, _ in perfiles)
        App(root, Juego(replace(conf, cocineros=nombres)), dict(perfiles))

    PantallaInicio(root, conf.cocineros, empezar).grid(row=0, column=0, columnspan=2)
    root.mainloop()
