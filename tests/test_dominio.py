import unittest

from cocina.dominio.caja import Caja
from cocina.dominio.destinos import EnPuesto
from cocina.dominio.pedido import EN_ESPERA, PREPARANDO, Pedido
from cocina.dominio.receta import Receta
from cocina.dominio.tablero import Tablero

SOPA = Receta("Sopa", {"Tomate": 1}, (("Tablas", 1.0),), precio=8)


class RelojFalso:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class TestPedido(unittest.TestCase):
    def test_restante_baja_con_el_tiempo(self):
        reloj = RelojFalso()
        p = Pedido(SOPA, espera=35, ahora=reloj)
        self.assertEqual(p.restante(), 35)
        reloj.t += 40
        self.assertEqual(p.restante(), -5)

    def test_asignar(self):
        p = Pedido(SOPA, 35)
        self.assertEqual(p.estado, EN_ESPERA)
        p.asignar("Ana")
        self.assertEqual((p.estado, p.cocinero), (PREPARANDO, "Ana"))

    def test_ids_crecientes(self):
        a, b = Pedido(SOPA, 35), Pedido(SOPA, 35)
        self.assertEqual(b.id, a.id + 1)


class TestCaja(unittest.TestCase):
    def test_cobrar_a_tiempo_y_tarde(self):
        reloj = RelojFalso()
        caja = Caja(dinero_inicial=20, multa=3)
        p = Pedido(SOPA, espera=10, ahora=reloj)
        self.assertEqual(caja.cobrar(p, "Ana"), (8, True))
        reloj.t += 11
        self.assertEqual(caja.cobrar(p, "Ana"), (4, False))     # mitad de precio
        self.assertEqual((caja.dinero, caja.entregados), (32, 2))

    def test_multar(self):
        caja = Caja(20, 3)
        self.assertEqual(caja.multar(), 3)
        self.assertEqual((caja.dinero, caja.perdidos), (17, 1))

    def test_pagar_sin_dinero_no_descuenta(self):
        caja = Caja(5, 3)
        self.assertFalse(caja.pagar(6, "Jefe"))
        self.assertEqual(caja.dinero, 5)
        self.assertTrue(caja.pagar(5, "Jefe"))
        self.assertEqual(caja.dinero, 0)

    def test_resumen_parcial_es_por_servicio(self):
        caja = Caja(20, 3)
        caja.cobrar(Pedido(SOPA, 35), "Ana")
        caja.multar()
        self.assertEqual(caja.resumen_parcial(), (1, 1, 5))
        caja.multar()
        self.assertEqual(caja.resumen_parcial(), (0, 1, -3))

    def test_lock_libre_despues_de_usarlo(self):
        caja = Caja(20, 3)
        caja.multar()
        self.assertIsNone(caja.lock.dueno)


class TestTablero(unittest.TestCase):
    def test_respeta_el_maximo_sin_crear_pedidos_de_mas(self):
        t = Tablero(max_pedidos=2)
        creados = []

        def crear():
            p = Pedido(SOPA, 35)
            creados.append(p)
            return p

        self.assertIsNotNone(t.agregar(crear))
        self.assertIsNotNone(t.agregar(crear))
        self.assertIsNone(t.agregar(crear))
        self.assertEqual(len(creados), 2)            # no se gastó un número
        self.assertEqual(len(t.visibles()), 2)

    def test_siguiente_y_timeout(self):
        t = Tablero(5)
        p = t.agregar(lambda: Pedido(SOPA, 35))
        self.assertIs(t.siguiente(timeout=0.01), p)
        self.assertIsNone(t.siguiente(timeout=0.01))

    def test_quitar_y_sacar_pendientes(self):
        t = Tablero(5)
        a = t.agregar(lambda: Pedido(SOPA, 35))
        b = t.agregar(lambda: Pedido(SOPA, 35))
        t.quitar(a)
        t.quitar(a)                                  # quitar dos veces no falla
        self.assertEqual(t.visibles(), [b])
        self.assertEqual(list(t.sacar_pendientes()), [a, b])
        self.assertEqual(list(t.sacar_pendientes()), [])


class TestDestinos(unittest.TestCase):
    def test_son_valores(self):
        self.assertEqual(EnPuesto("Horno", 0), EnPuesto("Horno", 0))


if __name__ == "__main__":
    unittest.main()
