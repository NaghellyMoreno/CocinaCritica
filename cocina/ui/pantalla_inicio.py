"""Pantalla de inicio: elegir nombre y apariencia de cada cocinero."""

import time
import tkinter as tk
from dataclasses import replace
from tkinter import ttk

from ..dominio.actividad import Actividad
from .avatar.apariencia import (ACCESORIOS, COLORES_PELO, DELANTALES, PEINADOS,
                                PIELES, apariencia_aleatoria, apariencia_inicial)
from .avatar.dibujo import dibujar_avatar
from .avatar.poses import pose_para
from .perfiles import validar_nombres
from .tema import FONDO, ROJO, SUAVE, TEXTO

# Lo que hace el avatar de muestra, en ciclo: (actividad, estación)
DEMOS = (
    (Actividad.FIN, None),
    (Actividad.LAVANDO, None),
    (Actividad.COCINANDO, "Tablas"),
    (Actividad.COCINANDO, "Estufas"),
    (Actividad.ENTREGANDO, None),
    (Actividad.BARRERA, None),
)
SEGUNDOS_POR_DEMO = 2.5
ESCALA_MUESTRA = 1.8


class _Muestras:
    """Fila de cuadritos de color; el elegido lleva un marco oscuro."""

    def __init__(self, master, colores, al_elegir):
        self.frame = tk.Frame(master, bg=FONDO)
        self._marcos = {}
        for i, color in enumerate(colores):
            marco = tk.Frame(self.frame, bg=FONDO, padx=2, pady=2)
            marco.grid(row=i // 6, column=i % 6, padx=1, pady=1)
            cuadro = tk.Frame(marco, bg=color, width=16, height=16, cursor="hand2")
            cuadro.pack()
            for w in (marco, cuadro):
                w.bind("<Button-1>", lambda e, c=color: al_elegir(c))
            self._marcos[color] = marco

    def marcar(self, elegido):
        for color, marco in self._marcos.items():
            marco.configure(bg=TEXTO if color == elegido else FONDO)


class FichaCocinero:
    """Nombre, controles de apariencia y vista previa animada de un cocinero."""

    def __init__(self, master, numero, nombre, apariencia):
        self._ap = apariencia
        self.frame = ttk.LabelFrame(master, text=f"Cocinero {numero}")

        self.canvas = tk.Canvas(self.frame, width=170, height=175, bg=FONDO,
                                highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=2, pady=(4, 0))

        self.var_nombre = tk.StringVar(value=nombre)
        self._etiqueta(1, "Nombre")
        ttk.Entry(self.frame, textvariable=self.var_nombre, width=14).grid(
            row=1, column=1, sticky="w", padx=4, pady=3)

        self._etiqueta(2, "Piel")
        self._piel = _Muestras(self.frame, PIELES, lambda c: self._cambiar(piel=c))
        self._piel.frame.grid(row=2, column=1, sticky="w", padx=4)

        self._etiqueta(3, "Peinado")
        self.var_peinado = tk.StringVar(value=apariencia.peinado)
        cb = ttk.Combobox(self.frame, textvariable=self.var_peinado, values=PEINADOS,
                          state="readonly", width=12)
        cb.grid(row=3, column=1, sticky="w", padx=4, pady=3)
        cb.bind("<<ComboboxSelected>>",
                lambda e: self._cambiar(peinado=self.var_peinado.get()))

        self._etiqueta(4, "Pelo")
        self._pelo = _Muestras(self.frame, COLORES_PELO, lambda c: self._cambiar(pelo=c))
        self._pelo.frame.grid(row=4, column=1, sticky="w", padx=4)

        self._etiqueta(5, "Delantal")
        self._delantal = _Muestras(self.frame, DELANTALES,
                                   lambda c: self._cambiar(delantal=c))
        self._delantal.frame.grid(row=5, column=1, sticky="w", padx=4)

        self._etiqueta(6, "Accesorio")
        self.var_accesorio = tk.StringVar(value=apariencia.accesorio)
        cb = ttk.Combobox(self.frame, textvariable=self.var_accesorio,
                          values=ACCESORIOS, state="readonly", width=12)
        cb.grid(row=6, column=1, sticky="w", padx=4, pady=3)
        cb.bind("<<ComboboxSelected>>",
                lambda e: self._cambiar(accesorio=self.var_accesorio.get()))

        ttk.Button(self.frame, text="Aleatorio", command=self._aleatorio).grid(
            row=7, column=0, columnspan=2, pady=(4, 8))
        self._refrescar_controles()

    def _etiqueta(self, fila, texto):
        tk.Label(self.frame, text=texto, bg=FONDO, fg=SUAVE, anchor="e",
                 font=("Helvetica", 10)).grid(row=fila, column=0, sticky="e", padx=(8, 0))

    def _cambiar(self, **rasgos):
        self._ap = replace(self._ap, **rasgos)
        self._refrescar_controles()

    def _aleatorio(self):
        self._ap = apariencia_aleatoria()
        self._refrescar_controles()

    def _refrescar_controles(self):
        self._piel.marcar(self._ap.piel)
        self._pelo.marcar(self._ap.pelo)
        self._delantal.marcar(self._ap.delantal)
        self.var_peinado.set(self._ap.peinado)
        self.var_accesorio.set(self._ap.accesorio)

    def nombre(self):
        return self.var_nombre.get().strip()

    def apariencia(self):
        return self._ap

    def dibujar(self, t):
        actividad, estacion = DEMOS[int(t / SEGUNDOS_POR_DEMO) % len(DEMOS)]
        self.canvas.delete("all")
        dibujar_avatar(self.canvas, 62, 150, self._ap,
                       pose_para(actividad, estacion, t), t, escala=ESCALA_MUESTRA)
        self.canvas.create_text(62, 166, text=self.nombre() or "…", fill=TEXTO,
                                font=("Helvetica", 11, "bold"))


class PantallaInicio:
    def __init__(self, master, nombres, al_empezar):
        self._al_empezar = al_empezar
        self.frame = tk.Frame(master, bg=FONDO, padx=16, pady=12)

        tk.Label(self.frame, text="Cocina concurrente", bg=FONDO, fg=TEXTO,
                 font=("Helvetica", 20, "bold")).pack()
        tk.Label(self.frame, text="Personaliza a tus cocineros (cada uno es un hilo)",
                 bg=FONDO, fg=SUAVE, font=("Helvetica", 12)).pack(pady=(0, 10))

        columnas = tk.Frame(self.frame, bg=FONDO)
        columnas.pack()
        self._fichas = []
        for k, nombre in enumerate(nombres):
            ficha = FichaCocinero(columnas, k + 1, nombre, apariencia_inicial(k))
            ficha.frame.grid(row=0, column=k, padx=8, sticky="n")
            self._fichas.append(ficha)

        self.lbl_error = tk.Label(self.frame, text="", bg=FONDO, fg=ROJO,
                                  font=("Helvetica", 11, "bold"))
        self.lbl_error.pack(pady=(10, 0))
        ttk.Button(self.frame, text="¡A cocinar!", command=self._empezar).pack(pady=8)

        self._tarea = None
        self._animar()

    def grid(self, **opciones):
        self.frame.grid(**opciones)

    def _animar(self):
        t = time.time()
        for f in self._fichas:
            f.dibujar(t)
        self._tarea = self.frame.after(40, self._animar)

    def _empezar(self):
        error = validar_nombres([f.nombre() for f in self._fichas])
        if error:
            self.lbl_error.configure(text=error)
            return
        perfiles = [(f.nombre(), f.apariencia()) for f in self._fichas]
        self.frame.after_cancel(self._tarea)
        self.frame.destroy()
        self._al_empezar(perfiles)
