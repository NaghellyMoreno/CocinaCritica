"""Avatares: poses, dibujo (sobre un canvas falso, sin ventana) y perfiles."""

import random
import unittest
from itertools import product

from cocina.dominio.actividad import Actividad
from cocina.ui.avatar import dibujo
from cocina.ui.avatar.apariencia import (ACCESORIOS, PEINADOS, Apariencia,
                                         apariencia_aleatoria, apariencia_inicial)
from cocina.ui.avatar.poses import ACCIONES_ESTACION, POSES, Pose, pose_para
from cocina.ui.perfiles import validar_nombres


class CanvasFalso:
    """Imita los create_* de tk.Canvas y solo cuenta lo que se dibuja."""

    def __init__(self):
        self.items = []

    def __getattr__(self, nombre):
        if not nombre.startswith("create_"):
            raise AttributeError(nombre)

        def crear(*coords, **opciones):
            self.items.append((nombre, coords, opciones))
        return crear


class TestPoses(unittest.TestCase):
    def test_hay_pose_para_cada_actividad(self):
        self.assertEqual(set(POSES), set(Actividad))

    def test_todas_las_poses_en_varios_instantes(self):
        for actividad, t in product(Actividad, (0.0, 0.7, 3.3, 12.1)):
            for estacion in (None, *ACCIONES_ESTACION):
                pose = pose_para(actividad, estacion, t)
                self.assertIsInstance(pose, Pose)
                self.assertIn(pose.cara, dibujo.CARAS)
                self.assertTrue(set(pose.efectos) <= set(dibujo.EFECTOS))
                if pose.objeto not in (None, "plato"):
                    self.assertIn(pose.objeto, dibujo.OBJETOS)

    def test_cada_estacion_tiene_su_herramienta(self):
        herramientas = {e: pose_para(Actividad.COCINANDO, e, 1.0).objeto
                        for e in ACCIONES_ESTACION}
        self.assertEqual(herramientas, {"Tablas": "cuchillo", "Estufas": "cuchara",
                                        "Horno": "pala"})

    def test_caminar_manda_sobre_la_actividad(self):
        pose = pose_para(Actividad.COCINANDO, "Tablas", 1.0, caminando=True,
                         direccion=1)
        self.assertIsNone(pose.objeto)
        self.assertEqual(pose.mirada, 1)

    def test_feliz_despues_de_entregar(self):
        self.assertEqual(pose_para(Actividad.LIBRE, None, 1.0, feliz=True).cara,
                         "feliz")
        # la preocupación no se borra con una sonrisa
        self.assertEqual(
            pose_para(Actividad.SIN_INGREDIENTES, None, 1.0, feliz=True).cara,
            "preocupado")

    def test_sin_actividad_esta_en_reposo(self):
        self.assertEqual(pose_para(None, None, 1.0).cara, "normal")


class TestDibujo(unittest.TestCase):
    def test_todas_las_combinaciones_se_dibujan(self):
        for peinado, accesorio in product(PEINADOS, ACCESORIOS):
            ap = Apariencia("#f1c27d", peinado, "#2c1b10", "#2e86ab", accesorio)
            for actividad in Actividad:
                cv = CanvasFalso()
                pose = pose_para(actividad, "Estufas", 2.0)
                dibujo.dibujar_avatar(cv, 100, 100, ap, pose, 2.0, escala=1.5)
                self.assertGreater(len(cv.items), 10)

    def test_todo_lleva_la_etiqueta(self):
        cv = CanvasFalso()
        dibujo.dibujar_avatar(cv, 0, 0, apariencia_inicial(0),
                              pose_para(Actividad.ENTREGANDO, None, 0.5), 0.5,
                              tag="ana")
        self.assertTrue(all(op["tags"] == "ana" for _, _, op in cv.items))

    def test_escala(self):
        chico, grande = CanvasFalso(), CanvasFalso()
        ap, pose = apariencia_inicial(1), Pose()
        dibujo.dibujar_avatar(chico, 0, 0, ap, pose, 0, escala=1)
        dibujo.dibujar_avatar(grande, 0, 0, ap, pose, 0, escala=2)
        sombra_chica, sombra_grande = chico.items[0][1], grande.items[0][1]
        self.assertEqual([c * 2 for c in sombra_chica], list(sombra_grande))

    def test_oscurecer(self):
        self.assertEqual(dibujo.oscurecer("#ffffff", 0.5), "#7f7f7f")


class TestApariencia(unittest.TestCase):
    def test_iniciales_conservan_los_colores_de_siempre(self):
        colores = [apariencia_inicial(k).delantal for k in range(3)]
        self.assertEqual(colores, ["#e4572e", "#2e86ab", "#7a5cc2"])

    def test_inicial_para_cocineros_extra(self):
        self.assertIsInstance(apariencia_inicial(7), Apariencia)

    def test_aleatoria_usa_opciones_validas(self):
        ap = apariencia_aleatoria(random.Random(3))
        self.assertIn(ap.peinado, PEINADOS)
        self.assertIn(ap.accesorio, ACCESORIOS)


class TestValidarNombres(unittest.TestCase):
    def test_validos(self):
        self.assertIsNone(validar_nombres(["Ana", "Luis", "Sofi"]))

    def test_vacio(self):
        self.assertIn("nombre", validar_nombres(["Ana", "  ", "Sofi"]))

    def test_repetido_sin_importar_mayusculas(self):
        self.assertIn("ana", validar_nombres(["Ana", "ana", "Sofi"]).lower())

    def test_muy_largo(self):
        self.assertIn("largo", validar_nombres(["Ana", "Maximiliano Jr", "Sofi"]))


if __name__ == "__main__":
    unittest.main()
