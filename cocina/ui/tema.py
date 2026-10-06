from tkinter import ttk

FONDO, LINEA, TEXTO, SUAVE = "#fbf7f0", "#b9ad9b", "#2b2620", "#7a6f62"
ROJO, VERDE, NARANJA = "#d64933", "#3a9d5d", "#e09f3e"


def configurar_estilos():
    """Estilos ttk compartidos por la pantalla de inicio y el juego."""
    st = ttk.Style()
    st.configure("TLabelframe", background=FONDO)
    st.configure("TLabelframe.Label", background=FONDO,
                 font=("Helvetica", 11, "bold"))


def aclarar(color, f=0.72):
    """Mezcla un color con blanco (tinte suave para los puestos ocupados)."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))
