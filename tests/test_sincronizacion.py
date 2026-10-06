"""Las dos estrategias, con hilos reales: la segura respeta los invariantes y
la ingenua los rompe (que es justo lo que el juego quiere mostrar)."""

import threading
import unittest

from cocina.concurrencia.sincronizacion import (SelectorSincronizacion,
                                                SincronizacionIngenua,
                                                SincronizacionSegura)
from cocina.dominio.destinos import EnPuesto, EnSobrecupo
from cocina.dominio.despensa import Despensa
from cocina.dominio.estacion import Estacion

SEGURA = SincronizacionSegura(pausa_contar=0.01)
INGENUA = SincronizacionIngenua(pausa=0.05, sondeo=0.005)


def en_paralelo(n, funcion):
    """Lanza `n` hilos que arrancan a la vez y espera a que terminen."""
    salida = threading.Barrier(n)
    resultados = [None] * n

    def correr(i):
        salida.wait()
        resultados[i] = funcion(i)

    hilos = [threading.Thread(target=correr, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=5)
    return resultados


class TestDespensa(unittest.TestCase):
    def test_segura_no_deja_stock_negativo(self):
        d = Despensa({"Tomate": 2}, pausa_reponer=0)
        tomados = en_paralelo(5, lambda i: d.tomar({"Tomate": 1}, f"c{i}", SEGURA))
        self.assertEqual(sum(tomados), 2)
        self.assertEqual(d.stock["Tomate"], 0)
        self.assertEqual(d.violaciones, 0)
        self.assertIsNone(d.lock.dueno)

    def test_ingenua_comparte_el_ultimo_tomate(self):
        d = Despensa({"Tomate": 1}, pausa_reponer=0)
        tomados = en_paralelo(3, lambda i: d.tomar({"Tomate": 1}, f"c{i}", INGENUA))
        self.assertGreater(sum(tomados), 1)
        self.assertLess(d.stock["Tomate"], 0)
        self.assertGreater(d.violaciones, 0)

    def test_sin_ingredientes_no_toma(self):
        d = Despensa({"Tomate": 0})
        self.assertFalse(d.tomar({"Tomate": 1}, "Ana", SEGURA))
        self.assertFalse(d.tomar({"Tomate": 1}, "Ana", INGENUA))

    def test_agregar(self):
        d = Despensa({"Tomate": 0}, pausa_reponer=0)
        d.agregar("Tomate", 3, "Jefe")
        self.assertEqual(d.foto(), {"Tomate": 3})


class TestEstacion(unittest.TestCase):
    def _usar(self, est, modo, quien):
        lugar = est.entrar(quien, "Sopa", 0.05, modo)
        maximo = est.ocupados()
        threading.Event().wait(0.05)
        est.salir(lugar)
        return maximo

    def test_segura_nunca_supera_la_capacidad(self):
        est = Estacion("Horno", "Horno", 1)
        maximos = en_paralelo(4, lambda i: self._usar(est, SEGURA, f"c{i}"))
        self.assertEqual(max(maximos), 1)
        f = est.foto()
        self.assertEqual((f.violaciones, f.usados, f.contador_semaforo), (0, 0, 1))

    def test_ingenua_genera_sobrecupo(self):
        est = Estacion("Horno", "Horno", 1)
        en_paralelo(3, lambda i: self._usar(est, INGENUA, f"c{i}"))
        f = est.foto()
        self.assertGreater(f.violaciones, 0)
        self.assertEqual(f.usados, 0)                 # todos salieron
        self.assertEqual(f.contador_semaforo, 1)      # nadie tocó el semáforo

    def test_destino_del_lugar(self):
        est = Estacion("Horno", "Horno", 1)
        primero = est.entrar("Ana", "Pizza", 1, SEGURA)
        self.assertEqual(primero.destino, EnPuesto("Horno", 0))
        # Con el puesto ocupado, alguien que entra sin esperar queda en sobrecupo
        segundo = est.entrar("Luis", "Pizza", 1, _SinEspera())
        self.assertEqual(segundo.destino, EnSobrecupo("Horno"))
        self.assertEqual(est.foto().usados, 2)
        est.salir(segundo)
        est.salir(primero)
        self.assertEqual(est.foto().usados, 0)
        self.assertEqual(est.contador_semaforo(), 1)


class _SinEspera(SincronizacionIngenua):
    """Entra directo, sin mirar si hay lugar (para provocar un sobrecupo)."""

    def ocupar_puesto(self, estacion):
        return False


class TestSelector(unittest.TestCase):
    def test_cambia_de_modo(self):
        s = SelectorSincronizacion(SEGURA, INGENUA)
        self.assertIs(s.actual, SEGURA)
        self.assertIs(s.usar(False), INGENUA)
        self.assertIs(s.actual, INGENUA)
        self.assertIs(s.usar(True), SEGURA)


if __name__ == "__main__":
    unittest.main()
