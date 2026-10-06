"""Una jornada completa, sin interfaz y con tiempos cortos."""

import time
import unittest
from dataclasses import replace

from cocina.config import Configuracion
from cocina.dominio.receta import Receta
from cocina.dominio.actividad import Actividad
from cocina.eventos import EstadoCocinero, FinJuego, PuedeAbrir, ResumenServicio
from cocina.juego.juego import Juego


def conf_rapida(**cambios):
    base = replace(
        Configuracion(),
        n_servicios=2, duracion_servicio=1.0, tiempo_pedido=5,
        intervalo_pedidos=(0.05, 0.1), pausa_ingenua=0.02, caminar=0.0,
        pausa_contar=0.0, pausa_reponer=0.0, sondeo_ingenuo=0.005,
        lavado=(0.0, 0.02), espera_pedido=0.02, reintento_ingredientes=0.02,
        stock_inicial={"Tomate": 50, "Cebolla": 50},
        precios={"Tomate": 1, "Cebolla": 1},
        recetas={"Sopa": Receta("Sopa", {"Tomate": 1, "Cebolla": 1},
                                (("Tablas", 0.05), ("Estufas", 0.05)), 8)},
    )
    return replace(base, **cambios)


def jugar(juego, limite=15):
    """Abre cada servicio apenas se puede y junta todos los eventos."""
    eventos = []
    juego.iniciar()
    fin = time.time() + limite
    while time.time() < fin:
        for e in juego.eventos_pendientes():
            eventos.append(e)
            if isinstance(e, PuedeAbrir):
                juego.abrir_servicio()
            if isinstance(e, FinJuego):
                return eventos
        time.sleep(0.01)
    raise AssertionError("la jornada no terminó a tiempo")


class TestJornada(unittest.TestCase):
    def test_modo_seguro_sin_violaciones(self):
        juego = Juego(conf_rapida())
        eventos = jugar(juego)
        resumenes = [e for e in eventos if isinstance(e, ResumenServicio)]
        self.assertEqual([r.servicio for r in resumenes], [1, 2])
        foto = juego.foto()
        self.assertEqual(foto.violaciones, 0)
        self.assertGreater(foto.entregados, 0)
        self.assertEqual(foto.dinero, 20 + sum(r.ganancia for r in resumenes))
        self.assertFalse(foto.abierto)

        actividades = {e.actividad for e in eventos if isinstance(e, EstadoCocinero)}
        for a in (Actividad.LAVANDO, Actividad.BARRERA, Actividad.BUSCANDO,
                  Actividad.EN_COLA, Actividad.COCINANDO, Actividad.ENTREGANDO,
                  Actividad.FIN):
            self.assertIn(a, actividades)
        cocinando = {e.estacion for e in eventos if isinstance(e, EstadoCocinero)
                     and e.actividad is Actividad.COCINANDO}
        self.assertEqual(cocinando, {"Tablas", "Estufas"})

    def test_compra(self):
        juego = Juego(conf_rapida(dinero_inicial=10))
        self.assertEqual(juego.opciones_compra(), [("Tomate", 3), ("Cebolla", 3)])
        juego._compras.comprar("Tomate")             # sin hilo, para no esperar
        foto = juego.foto()
        self.assertEqual((foto.dinero, foto.stock["Tomate"]), (7, 53))

    def test_compra_sin_dinero(self):
        juego = Juego(conf_rapida(dinero_inicial=2))
        juego._compras.comprar("Tomate")
        foto = juego.foto()
        self.assertEqual((foto.dinero, foto.stock["Tomate"]), (2, 50))

    def test_cambiar_modo_avisa(self):
        juego = Juego(conf_rapida())
        juego.usar_sincronizacion(False)
        juego.usar_sincronizacion(True)
        textos = [e.texto for e in juego.eventos_pendientes()]
        self.assertEqual(textos, ["*** Modo SIN sincronización activado ***",
                                  "*** Modo seguro activado ***"])


if __name__ == "__main__":
    unittest.main()
