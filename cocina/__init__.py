"""
COCINA CONCURRENTE — un juego estilo Overcooked para practicar hilos.

Paquetes:
- cocina.dominio ...... recursos compartidos y entidades (estación, despensa,
                        caja, tablero, pedido, receta)
- cocina.concurrencia . LockVisible, estrategias de sincronización y el
                        control de servicio (barreras y Events)
- cocina.juego ........ los hilos (jefe, cocineros, generador) y la fachada
                        `Juego` que arma todo
- cocina.ui ........... interfaz Tkinter (solo la usa el hilo principal)

Ver README.md para el mapa completo de conceptos del curso.
"""
