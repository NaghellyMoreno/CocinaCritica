"""Lienzo de la cocina: zonas, estaciones, pedidos y cocineros animados."""

import math
import random
import time
import tkinter as tk

from ..dominio.actividad import Actividad
from ..dominio.destinos import DESPENSA, LAVAMANOS, MOSTRADOR, EnZona
from ..dominio.pedido import PREPARANDO
from .avatar.dibujo import dibujar_avatar
from .avatar.poses import pose_para
from .layout import (ALTO, ANCHO, ORIGEN_ESTACIONES, PEDIDOS_XY, PUESTO_GAP,
                     PUESTO_H, PUESTO_W, SINGULAR, ZONAS, Posiciones,
                     pies_en_puesto, puesto_rect)
from .tema import FONDO, LINEA, NARANJA, ROJO, SUAVE, TEXTO, VERDE, aclarar

SEGUNDOS_FELIZ = 1.8      # cuánto sonríe un cocinero después de entregar


# --- aparatos de cada estación, relativos a los pies del cocinero en el puesto ---
def _tabla(cv, fx, fy):
    cv.create_rectangle(fx + 16, fy - 12, fx + 116, fy + 8, fill="#e8dccb",
                        outline=LINEA)
    cv.create_rectangle(fx + 22, fy - 24, fx + 108, fy - 12, fill="#d9a66b",
                        outline="#a87437")
    cv.create_oval(fx + 84, fy - 34, fx + 96, fy - 23, fill="#d64933", outline="")
    cv.create_line(fx + 90, fy - 34, fx + 92, fy - 37, fill=VERDE, width=2)


def _estufa(cv, fx, fy):
    cv.create_rectangle(fx + 16, fy - 26, fx + 116, fy + 8, fill="#5b6066",
                        outline="#3f4347")
    for kx in (fx + 40, fx + 60, fx + 80, fx + 100):
        cv.create_oval(kx - 3, fy - 6, kx + 3, fy, fill="#c9ccd1", outline="")
    cv.create_rectangle(fx + 28, fy - 42, fx + 68, fy - 26, fill="#8a8f98",
                        outline="#5d6168")
    cv.create_line(fx + 22, fy - 38, fx + 28, fy - 38, fill="#5d6168", width=3)
    cv.create_line(fx + 68, fy - 38, fx + 74, fy - 38, fill="#5d6168", width=3)
    cv.create_oval(fx + 80, fy - 31, fx + 106, fy - 25, fill="#3a3a3a", outline="")
    cv.create_line(fx + 106, fy - 28, fx + 116, fy - 30, fill="#3a3a3a", width=3)


def _horno(cv, fx, fy):
    cv.create_rectangle(fx + 26, fy - 50, fx + 116, fy + 8, fill="#8d5b4c",
                        outline="#6d4337")
    cv.create_rectangle(fx + 36, fy - 38, fx + 106, fy - 8, fill="#2f2f2f",
                        outline="#1f1f1f", tags="ventana_horno")
    cv.create_line(fx + 44, fy - 44, fx + 98, fy - 44, fill="#c9ccd1", width=3)


APARATOS = {"Tablas": _tabla, "Estufas": _estufa, "Horno": _horno}


# --- cómo se ve un aparato mientras alguien lo usa ---------------------------------
def _estufa_encendida(cv, fx, fy, t):
    for i in range(3):
        x = fx + 34 + i * 14
        alto = 4 + math.sin(t * 15 + i) * 2
        cv.create_polygon(x - 4, fy - 26, x, fy - 26 - alto, x + 4, fy - 26,
                          fill="#f4a261", outline="", tags="dyn")


def _horno_encendido(cv, fx, fy, t):
    brillo = "#f4a261" if math.sin(t * 4) > 0 else "#e76f51"
    cv.create_rectangle(fx + 37, fy - 37, fx + 105, fy - 9, fill=brillo,
                        outline="", tags="dyn")


APARATOS_ENCENDIDOS = {"Estufas": _estufa_encendida, "Horno": _horno_encendido}


class _EnEscena:
    """Lo que la vista recuerda de cada cocinero para animarlo."""

    def __init__(self, nombre, apariencia):
        self.nombre = nombre
        self.ap = apariencia
        self.destino = EnZona(LAVAMANOS)
        self.x = self.y = 0.0
        self.actividad = None          # None = en camino o sin noticias aún
        self.estacion = None
        self.caminando = False
        self.direccion = 0.0
        self.feliz_hasta = 0.0
        self.fase = random.uniform(0, 10)   # para que no se muevan al unísono


class VistaCocina:
    def __init__(self, master, cocineros, apariencias, estaciones):
        self.canvas = tk.Canvas(master, width=ANCHO, height=ALTO, bg=FONDO,
                                highlightthickness=0)
        self._colores = {n: apariencias[n].delantal for n in cocineros}
        self._posiciones = Posiciones(cocineros)
        self._dibujar_fijo(estaciones)

        self._cocineros = {n: _EnEscena(n, apariencias[n]) for n in cocineros}
        for c in self._cocineros.values():
            c.x, c.y = self._posiciones.xy(c.nombre, c.destino, None)
        self._banner = None

    def grid(self, **opciones):
        self.canvas.grid(**opciones)

    def mover(self, nombre, destino):
        c = self._cocineros[nombre]
        c.destino = destino
        c.actividad, c.estacion = None, None

    def cambiar_actividad(self, nombre, actividad, estacion):
        c = self._cocineros[nombre]
        c.actividad, c.estacion = actividad, estacion
        if actividad is Actividad.ENTREGANDO:
            c.feliz_hasta = time.time() + SEGUNDOS_FELIZ

    def mostrar_banner(self, texto, segundos):
        self._banner = (texto, time.time() + segundos)

    def actualizar(self, foto):
        ahora = time.time()
        self._animar(foto)
        self._dibujar_dinamico(foto, ahora)
        self._dibujar_avatares(ahora)
        self._dibujar_banner(ahora)

    # ---------- partes fijas ----------
    def _dibujar_fijo(self, estaciones):
        cv = self.canvas
        for nombre, (x0, y0, x1, y1) in ZONAS.items():
            cv.create_rectangle(x0, y0, x1, y1, fill="#f1e9dc", outline=LINEA, width=2)
            cv.create_text(x0 + 8, y0 + 12, text=nombre, anchor="w",
                           font=("Helvetica", 11, "bold"), fill=TEXTO)
        self._dibujar_lavamanos_fijo()
        for clave, est in estaciones.items():
            for i in range(est.capacidad):
                r = puesto_rect(clave, i)
                cv.create_rectangle(*r, fill="white", outline=LINEA, width=2)
                cv.create_text(r[0] + 6, r[1] + 10, anchor="w",
                               text=f"{SINGULAR[clave]} {i + 1}",
                               font=("Helvetica", 9), fill=SUAVE)
                if clave in APARATOS:
                    APARATOS[clave](cv, *pies_en_puesto(clave, i))
        x, y = PEDIDOS_XY
        cv.create_text(x, y - 22, anchor="w", text="Pedidos",
                       font=("Helvetica", 11, "bold"), fill=TEXTO)

    def _dibujar_lavamanos_fijo(self):
        cv = self.canvas
        x0, y0, x1, y1 = ZONAS[LAVAMANOS]
        cx, cy = x1 - 26, y0 + 22
        cv.create_line(cx - 6, cy - 12, cx - 6, cy - 16, cx + 6, cy - 16, cx + 6, cy - 9,
                       fill="#9aa3ab", width=3)
        cv.create_arc(cx - 14, cy - 14, cx + 14, cy + 10, start=180, extent=180,
                      style="chord", fill="#dbe9f1", outline="#9aa3ab", width=2)

    # ---------- animación de los cocineros ----------
    def _animar(self, foto):
        """Acerca a cada cocinero un poco hacia su destino."""
        for c in self._cocineros.values():
            tx, ty = self._posiciones.xy(c.nombre, c.destino, foto)
            dx, dy = tx - c.x, ty - c.y
            c.x += dx * 0.25
            c.y += dy * 0.25
            c.caminando = math.hypot(dx, dy) > 3
            if c.caminando and abs(dx) > 1:
                c.direccion = 1.0 if dx > 0 else -1.0
            elif not c.caminando:
                c.direccion = 0.0

    def _dibujar_avatares(self, ahora):
        cv = self.canvas
        cv.delete("avatar")
        # los de más abajo se dibujan al final: quedan "delante"
        for c in sorted(self._cocineros.values(), key=lambda c: c.y):
            t = ahora + c.fase
            pose = pose_para(c.actividad, c.estacion, t, caminando=c.caminando,
                             direccion=c.direccion, feliz=ahora < c.feliz_hasta)
            dibujar_avatar(cv, c.x, c.y, c.ap, pose, t, tag="avatar")
            cv.create_text(c.x, c.y + 10, text=c.nombre, fill=TEXTO, tags="avatar",
                           font=("Helvetica", 9, "bold"))

    # ---------- partes que cambian ----------
    def _dibujar_dinamico(self, foto, ahora):
        self.canvas.delete("dyn")
        self._dibujar_lavamanos(foto)
        self._dibujar_despensa(foto)
        self._dibujar_mostrador(foto)
        self._dibujar_estaciones(foto, ahora)
        self._dibujar_pedidos(foto)

    def _dibujar_lavamanos(self, foto):
        # Lavamanos = barrera
        x0, y0, x1, y1 = ZONAS[LAVAMANOS]
        if foto.abierto:
            txt = "Servicio en curso"
        else:
            b = (foto.barrera_fin if foto.cierre_activo and foto.servicio
                 else foto.barrera_inicio)
            txt = f"Barrera: {b.esperando}/{b.partes} esperando"
        self.canvas.create_text(x0 + 8, y0 + 32, anchor="w", text=txt, tags="dyn",
                                font=("Helvetica", 10), fill=SUAVE)

    def _dibujar_despensa(self, foto):
        # Despensa = lock
        cv = self.canvas
        x0, y0, x1, y1 = ZONAS[DESPENSA]
        dueno = foto.dueno_despensa
        cv.create_text(x0 + 8, y0 + 32, anchor="w", tags="dyn",
                       text=f"Lock: {dueno if dueno else 'libre'}",
                       font=("Helvetica", 10, "bold"),
                       fill=ROJO if dueno else VERDE)
        for k, (ing, n) in enumerate(foto.stock.items()):
            cv.create_text(x0 + 98 + (k % 2) * 68, y0 + 14 + (k // 2) * 16,
                           anchor="w", tags="dyn", text=f"{ing} {n}",
                           font=("Helvetica", 9, "bold"),
                           fill=ROJO if n < 0 else (NARANJA if n == 0 else TEXTO))

    def _dibujar_mostrador(self, foto):
        x0, y0, x1, y1 = ZONAS[MOSTRADOR]
        self.canvas.create_text(x0 + 8, y0 + 32, anchor="w", tags="dyn",
                                text=f"Entregados: {foto.entregados}",
                                font=("Helvetica", 10), fill=SUAVE)

    def _dibujar_estaciones(self, foto, ahora):
        # Estaciones = semáforos
        cv = self.canvas
        for clave, est in foto.estaciones.items():
            x0, y0 = ORIGEN_ESTACIONES[clave]
            cap = est.capacidad
            libres = cap - est.usados
            cv.create_text(x0, y0 - 22, anchor="w", tags="dyn",
                           text=f"{est.etiqueta}  ·  Semáforo({cap})  ·  libres: {libres}",
                           font=("Helvetica", 11, "bold"),
                           fill=ROJO if libres < 0 else TEXTO)
            for i, d in enumerate(est.puestos):
                if d is None:
                    continue
                r = puesto_rect(clave, i)
                color = self._colores[d.cocinero]
                cv.create_rectangle(r[0] + 2, r[1] + 2, r[2] - 2, r[3] - 2,
                                    outline=color, width=3, tags="dyn")
                cv.create_rectangle(r[0] + 58, r[1] + 4, r[2] - 4, r[1] + 40,
                                    fill=aclarar(color), outline="", tags="dyn")
                cv.create_text(r[0] + 62, r[1] + 14, anchor="w", tags="dyn",
                               text=d.plato, font=("Helvetica", 10, "bold"),
                               fill=TEXTO)
                prog = min(1.0, (ahora - d.inicio) / d.duracion)
                cv.create_rectangle(r[0] + 62, r[1] + 26, r[2] - 8, r[1] + 34,
                                    fill="white", outline=LINEA, tags="dyn")
                cv.create_rectangle(r[0] + 62, r[1] + 26,
                                    r[0] + 62 + (r[2] - r[0] - 70) * prog, r[1] + 34,
                                    fill=VERDE, outline="", tags="dyn")
                if clave in APARATOS_ENCENDIDOS:
                    APARATOS_ENCENDIDOS[clave](cv, *pies_en_puesto(clave, i), ahora)
            if est.sobrecupo:
                ancho = cap * PUESTO_W + (cap - 1) * PUESTO_GAP
                yb = y0 + PUESTO_H + 6
                cv.create_rectangle(x0, yb, x0 + ancho, yb + 32, fill="#f6d5cf",
                                    outline=ROJO, width=2, tags="dyn")
                cv.create_text(x0 + ancho - 8, yb + 16, anchor="e", tags="dyn",
                               text="¡SOBRECUPO!", font=("Helvetica", 10, "bold"),
                               fill=ROJO)

    def _dibujar_pedidos(self, foto):
        cv = self.canvas
        px, py = PEDIDOS_XY
        for k, p in enumerate(foto.pedidos[:foto.max_pedidos]):
            x = px + (k % 3) * 120
            y = py + (k // 3) * 100
            resto = max(0.0, p.restante())
            frac = resto / p.espera
            col = VERDE if frac > 0.5 else (NARANJA if frac > 0.2 else ROJO)
            cv.create_rectangle(x, y, x + 112, y + 88, fill="white", outline=LINEA,
                                width=2, tags="dyn")
            cv.create_text(x + 6, y + 13, anchor="w", text=p.receta.nombre,
                           font=("Helvetica", 10, "bold"), fill=TEXTO, tags="dyn")
            cv.create_text(x + 6, y + 32, anchor="w", tags="dyn",
                           text=f"#{p.id} · ${p.receta.precio} · {resto:3.0f}s",
                           font=("Helvetica", 9), fill=SUAVE)
            quien = p.cocinero if p.estado == PREPARANDO else "en espera"
            cv.create_text(x + 6, y + 50, anchor="w", text=quien, tags="dyn",
                           font=("Helvetica", 9, "italic"),
                           fill=self._colores.get(p.cocinero, SUAVE))
            cv.create_rectangle(x + 6, y + 70, x + 6 + 100 * frac, y + 78, fill=col,
                                outline="", tags="dyn")

    def _dibujar_banner(self, ahora):
        self.canvas.delete("banner")
        if self._banner:
            texto, hasta = self._banner
            if ahora < hasta:
                self.canvas.create_rectangle(150, 320, 590, 390, fill=TEXTO,
                                             outline="", tags="banner")
                self.canvas.create_text(370, 355, text=texto, fill="white",
                                        tags="banner", font=("Helvetica", 14, "bold"))
