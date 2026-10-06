"""
Dibujo vectorial de un avatar en un tk.Canvas.

Peinados, accesorios, caras, objetos y efectos son tablas de funciones:
para agregar uno nuevo basta con escribir su función y registrarla.
"""

import math

PANTALON = "#3d3d4d"
ZAPATO = "#2b2620"
CAMISA = "#ffffff"
CONTORNO = "#b9ad9b"
TINTA = "#2b2620"
BOCA = "#8b2e2e"


def oscurecer(color, f=0.75):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c * f) for c in (r, g, b))


class Lapiz:
    """Dibuja con coordenadas relativas a los pies del avatar, ya escaladas."""

    def __init__(self, canvas, x, y, escala, tag):
        self.cv, self.x, self.y, self.s, self.tag = canvas, x, y, escala, tag

    def _xy(self, puntos):
        out = []
        for px, py in puntos:
            out += [self.x + px * self.s, self.y + py * self.s]
        return out

    def _ancho(self, w):
        return max(1.0, w * self.s)

    def ovalo(self, cx, cy, rx, ry, **kw):
        self.cv.create_oval(*self._xy([(cx - rx, cy - ry), (cx + rx, cy + ry)]),
                            tags=self.tag, **kw)

    def rect(self, x0, y0, x1, y1, **kw):
        self.cv.create_rectangle(*self._xy([(x0, y0), (x1, y1)]), tags=self.tag, **kw)

    def poligono(self, *puntos, **kw):
        self.cv.create_polygon(*self._xy(puntos), tags=self.tag, **kw)

    def linea(self, *puntos, ancho=1.0, **kw):
        self.cv.create_line(*self._xy(puntos), width=self._ancho(ancho),
                            capstyle="round", tags=self.tag, **kw)

    def arco(self, cx, cy, rx, ry, inicio, extension, ancho=1.0, **kw):
        self.cv.create_arc(*self._xy([(cx - rx, cy - ry), (cx + rx, cy + ry)]),
                           start=inicio, extent=extension,
                           width=self._ancho(ancho), tags=self.tag, **kw)

    def texto(self, x, y, texto, tamano, **kw):
        self.cv.create_text(*self._xy([(x, y)]), text=texto, tags=self.tag,
                            font=("Helvetica", max(6, int(tamano * self.s)), "bold"),
                            **kw)


# --- peinados: (parte detrás de la cabeza, parte encima) ------------------------
def _gorra_de_pelo(l, hx, hy, color):
    l.arco(hx, hy - 3, 10, 8, 0, 180, style="chord", fill=color, outline="")
    l.ovalo(hx - 8.5, hy - 2, 2, 4, fill=color, outline="")
    l.ovalo(hx + 8.5, hy - 2, 2, 4, fill=color, outline="")


def _largo_detras(l, hx, hy, color):
    l.poligono((hx - 11, hy - 4), (hx + 11, hy - 4), (hx + 12, hy + 12),
               (hx - 12, hy + 12), fill=color, outline="")


def _cola_detras(l, hx, hy, color):
    l.ovalo(hx + 12, hy + 3, 3.5, 8, fill=color, outline="")


def _rizos(l, hx, hy, color):
    for grados in range(160, 0, -28):
        a = math.radians(grados)
        l.ovalo(hx + math.cos(a) * 9, hy - 2 - math.sin(a) * 8, 4, 4,
                fill=color, outline="")


def _orejas_con_pelo(l, hx, hy, color):
    l.ovalo(hx - 9, hy - 1, 1.8, 3.5, fill=color, outline="")
    l.ovalo(hx + 9, hy - 1, 1.8, 3.5, fill=color, outline="")


PEINADOS = {
    "Corto": (None, _gorra_de_pelo),
    "Largo": (_largo_detras, _gorra_de_pelo),
    "Cola": (_cola_detras, _gorra_de_pelo),
    "Rizado": (None, _rizos),
    "Calvo": (None, _orejas_con_pelo),
}


# --- accesorios -----------------------------------------------------------------
def _gorro_de_chef(l, hx, hy, ap):
    for dx, dy, r in ((-6, -15, 5), (6, -15, 5), (0, -18, 7)):
        l.ovalo(hx + dx, hy + dy, r + 2, r, fill="white", outline=CONTORNO)
    l.rect(hx - 8, hy - 13, hx + 8, hy - 7, fill="white", outline=CONTORNO)


def _panuelo(l, hx, hy, ap):
    rojo = "#c0392b"
    l.arco(hx, hy - 3, 10.5, 8.5, 0, 180, style="chord", fill=rojo, outline="")
    l.poligono((hx + 8, hy - 5), (hx + 15, hy - 8), (hx + 14, hy - 1), fill=rojo,
               outline="")
    for dx in (-4, 3):
        l.ovalo(hx + dx, hy - 7, 1, 1, fill="white", outline="")


def _lentes(l, hx, hy, ap):
    for dx in (-3.8, 3.8):
        l.ovalo(hx + dx, hy - 1, 3.4, 3.2, outline=TINTA, width=max(1, l.s))
    l.linea((hx - 0.6, hy - 1.5), (hx + 0.6, hy - 1.5), ancho=1, fill=TINTA)


def _bigote(l, hx, hy, ap):
    l.poligono((hx - 5.5, hy + 3.5), (hx, hy + 1.5), (hx + 5.5, hy + 3.5),
               (hx + 2.5, hy + 4.8), (hx, hy + 3.6), (hx - 2.5, hy + 4.8),
               fill=ap.pelo, outline="", smooth=True)


ACCESORIOS = {
    "Gorro de chef": _gorro_de_chef,
    "Pañuelo": _panuelo,
    "Lentes": _lentes,
    "Bigote": _bigote,
    "Ninguno": lambda l, hx, hy, ap: None,
}


# --- caras ------------------------------------------------------------------------
def _ojos(l, hx, hy, mirada):
    for dx in (-3.5, 3.5):
        l.ovalo(hx + dx + mirada * 1.2, hy - 1, 1.3, 1.7, fill=TINTA, outline="")


def _ojos_felices(l, hx, hy):
    for dx in (-3.5, 3.5):
        l.arco(hx + dx, hy, 2, 1.8, 20, 140, ancho=1.3, style="arc", outline=TINTA)


def _ojos_entrecerrados(l, hx, hy):
    for dx in (-3.5, 3.5):
        l.linea((hx + dx - 1.8, hy - 0.5), (hx + dx + 1.8, hy - 0.5), ancho=1.3,
                fill=TINTA)


def _sonrisa(l, hx, hy):
    l.arco(hx, hy + 3.5, 3.5, 2.5, 200, 140, ancho=1.2, style="arc", outline=TINTA)


def _boca_recta(l, hx, hy):
    l.linea((hx - 2.5, hy + 4.5), (hx + 2.5, hy + 4.5), ancho=1.2, fill=TINTA)


def _cara_normal(l, hx, hy, mirada):
    _ojos(l, hx, hy, mirada)
    _sonrisa(l, hx, hy)


def _cara_feliz(l, hx, hy, mirada):
    _ojos_felices(l, hx, hy)
    l.arco(hx, hy + 3, 4, 3.5, 180, 180, style="chord", fill=BOCA, outline="")
    for dx in (-6, 6):
        l.ovalo(hx + dx, hy + 2, 1.8, 1.2, fill="#f4a6a6", outline="")


def _cara_concentrada(l, hx, hy, mirada):
    _ojos(l, hx, hy, mirada)
    _boca_recta(l, hx, hy)


def _cara_preocupada(l, hx, hy, mirada):
    _ojos(l, hx, hy, mirada)
    l.linea((hx - 5.5, hy - 4), (hx - 1.8, hy - 5.8), ancho=1.2, fill=TINTA)
    l.linea((hx + 1.8, hy - 5.8), (hx + 5.5, hy - 4), ancho=1.2, fill=TINTA)
    l.arco(hx, hy + 6.5, 3.5, 2.5, 20, 140, ancho=1.2, style="arc", outline=TINTA)


def _cara_aburrida(l, hx, hy, mirada):
    _ojos_entrecerrados(l, hx, hy)
    _boca_recta(l, hx, hy)


def _cara_bostezo(l, hx, hy, mirada):
    _ojos_entrecerrados(l, hx, hy)
    l.ovalo(hx, hy + 4.5, 2.2, 2.8, fill=BOCA, outline="")


def _cara_impaciente(l, hx, hy, mirada):
    _ojos(l, hx, hy, mirada)
    l.linea((hx - 5.5, hy - 5.5), (hx - 1.8, hy - 4.2), ancho=1.2, fill=TINTA)
    l.linea((hx + 1.8, hy - 4.2), (hx + 5.5, hy - 5.5), ancho=1.2, fill=TINTA)
    _boca_recta(l, hx, hy)


CARAS = {
    "normal": _cara_normal,
    "feliz": _cara_feliz,
    "concentrado": _cara_concentrada,
    "preocupado": _cara_preocupada,
    "aburrido": _cara_aburrida,
    "bostezo": _cara_bostezo,
    "impaciente": _cara_impaciente,
}


# --- objetos en la mano derecha ----------------------------------------------------
def _cuchillo(l, mx, my):
    l.linea((mx - 3, my + 1), (mx + 1, my), ancho=3, fill="#6b4226")
    l.linea((mx + 1, my), (mx + 12, my - 3), ancho=2.2, fill="#aab2ba")


def _cuchara(l, mx, my):
    l.linea((mx, my), (mx + 12, my - 2), ancho=2, fill="#8b5a2b")
    l.ovalo(mx + 13, my - 2, 2.5, 1.5, fill="#8b5a2b", outline="")


def _pala(l, mx, my):
    l.linea((mx - 6, my + 1), (mx + 18, my - 1), ancho=2, fill="#8b5a2b")
    l.poligono((mx + 18, my - 4), (mx + 31, my - 4), (mx + 31, my + 2),
               (mx + 18, my + 2), fill="#c49a6c", outline="")
    l.ovalo(mx + 24.5, my - 5, 6, 2, fill="#e9c46a", outline="#d64933")


OBJETOS = {"cuchillo": _cuchillo, "cuchara": _cuchara, "pala": _pala}


def _plato(l, pose, b):
    """El plato va entre las dos manos, por eso se dibuja antes que ellas."""
    cx = (pose.mano_izq[0] + pose.mano_der[0]) / 2
    cy = (pose.mano_izq[1] + pose.mano_der[1]) / 2 + b - 2
    l.arco(cx, cy, 7, 7, 0, 180, style="chord", fill="#e09f3e", outline="")
    l.ovalo(cx, cy, 11, 3, fill="white", outline=CONTORNO)


# --- efectos --------------------------------------------------------------------
def _burbujas(l, t, c):
    cx = (c["mano_izq"][0] + c["mano_der"][0]) / 2
    cy = c["mano_izq"][1]
    for i in range(5):
        f = (t * 0.7 + i / 5) % 1
        r = 1.5 + (i % 3) * 0.8
        l.ovalo(cx + math.sin(i * 1.9 + t * 2) * 7, cy - 4 - f * 26, r, r,
                fill="#eaf6fd", outline="#5fa8d3")


def _vapor(l, t, c):
    for i in range(3):
        f = (t * 0.5 + i / 3) % 1
        r = 3 + f * 4
        l.ovalo(46 + math.sin(t * 2 + i) * 4, -44 - f * 12, r * 0.7, r * 0.7,
                fill="#f4f4f4", outline="#d0d0d0")


def _picados(l, t, c):
    colores = ("#d64933", "#3a9d5d", "#e09f3e", "#d64933")
    for i, color in enumerate(colores):
        f = (t * 2 + i / 4) % 1
        x, y = 30 + i * 5, -26 - math.sin(f * math.pi) * 7
        l.rect(x - 1.2, y - 1.2, x + 1.2, y + 1.2, fill=color, outline="")


def _calor(l, t, c):
    for i in range(3):
        puntos = [(52 + i * 14 + math.sin(t * 5 + j + i) * 2, -50 - j * 4)
                  for j in range(5)]
        l.linea(*puntos, ancho=1.5, fill="#f4a261", smooth=True)


def _sudor(l, t, c):
    hx, hy = c["cabeza"]
    x, y = hx + 11, hy - 4 + (t * 1.5 % 1) * 8
    l.poligono((x, y - 3), (x + 2, y + 1), (x, y + 2.5), (x - 2, y + 1),
               fill="#7cc6f2", outline="#3a8fc7", smooth=True)


def _alerta(l, t, c):
    hx, hy = c["cabeza"]
    l.texto(hx, hy - 26 + math.sin(t * 6), "!", 13, fill="#d64933")


def _zzz(l, t, c):
    hx, hy = c["cabeza"]
    for i in range(2):
        f = (t * 0.5 + i / 2) % 1
        l.texto(hx + 10 + f * 8, hy - 12 - f * 14, "z", 7 + f * 3, fill="#7a6f62")


def _estrellas(l, t, c):
    for i in range(3):
        a = t * 3 + i * 2.1
        l.texto(math.cos(a) * 15, -70 + math.sin(a) * 5, "★", 8, fill="#e9b949")


EFECTOS = {
    "burbujas": _burbujas,
    "vapor": _vapor,
    "picados": _picados,
    "calor": _calor,
    "sudor": _sudor,
    "alerta": _alerta,
    "zzz": _zzz,
    "estrellas": _estrellas,
}


# --- el avatar completo -------------------------------------------------------------
def dibujar_avatar(canvas, x, y, ap, pose, t, escala=1.0, tag="avatar"):
    """Dibuja el avatar con los pies en (x, y)."""
    l = Lapiz(canvas, x, y, escala, tag)
    b = pose.rebote
    piel_borde = oscurecer(ap.piel)

    l.ovalo(0, 0, 13, 3, fill="#e3d9ca", outline="")                  # sombra

    for cadera, (px, alto) in ((-5, pose.pie_izq), (5, pose.pie_der)):  # piernas
        l.linea((cadera, -12 + b), (px, -1 - alto), ancho=4, fill=PANTALON)
        l.ovalo(px, -1 - alto, 3.5, 2, fill=ZAPATO, outline="")

    l.poligono((-8, -33 + b), (8, -33 + b), (11, -28 + b), (11, -12 + b),    # camisa
               (-11, -12 + b), (-11, -28 + b), fill=CAMISA, outline=CONTORNO)
    l.poligono((-7, -28 + b), (7, -28 + b), (9, -12 + b), (-9, -12 + b),      # delantal
               fill=ap.delantal, outline=oscurecer(ap.delantal))
    l.linea((-3, -22 + b), (3, -22 + b), ancho=1, fill=oscurecer(ap.delantal))

    if pose.objeto == "plato":
        _plato(l, pose, b)
    for hombro, (mx, my) in ((-9, pose.mano_izq), (9, pose.mano_der)):  # brazos
        l.linea((hombro, -29 + b), (mx, my + b), ancho=5, fill=CONTORNO)
        l.linea((hombro, -29 + b), (mx, my + b), ancho=3.5, fill=CAMISA)
        l.ovalo(mx, my + b, 3, 3, fill=ap.piel, outline=piel_borde)
    if pose.objeto in OBJETOS:
        mx, my = pose.mano_der
        OBJETOS[pose.objeto](l, mx, my + b)

    hx, hy = 0, -41 + b                                                   # cabeza
    detras, encima = PEINADOS.get(ap.peinado, PEINADOS["Corto"])
    if detras:
        detras(l, hx, hy, ap.pelo)
    l.ovalo(hx, hy, 9, 9, fill=ap.piel, outline=piel_borde)
    encima(l, hx, hy, ap.pelo)
    CARAS.get(pose.cara, _cara_normal)(l, hx, hy, pose.mirada)
    ACCESORIOS.get(ap.accesorio, ACCESORIOS["Ninguno"])(l, hx, hy, ap)

    contexto = {"cabeza": (hx, hy), "mano_izq": pose.mano_izq,
                "mano_der": pose.mano_der}
    for efecto in pose.efectos:
        EFECTOS[efecto](l, t, contexto)
