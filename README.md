# Cocina concurrente

Un juego estilo Overcooked para practicar hilos, locks, semáforos y barreras.

## ¿De qué se trata?

Eres el jefe de cocina. Tres cocineros (cada uno es un HILO) toman pedidos y
los preparan solos. Tu trabajo es abrir cada servicio y comprar ingredientes a
tiempo para que no se queden sin qué cocinar. Ganas dinero entregando pedidos
antes de que venzan.

## ¿Cómo jugar?

### 1. Elige a tus cocineros

Al abrir el juego aparece una pantalla de inicio. Para cada cocinero puedes
cambiar el **nombre** y la **apariencia**:

- tono de piel
- peinado y color de pelo
- color del delantal (también es su color en los paneles)
- un accesorio: gorro de chef, pañuelo, lentes o bigote

El botón *Aleatorio* sortea un diseño. Los nombres no pueden quedar vacíos,
repetirse ni pasar de 12 letras. Cuando estés listo, pulsa **¡A cocinar!**

### 2. Abre el servicio

La jornada tiene **3 servicios de 60 segundos**. Los cocineros se lavan las
manos y esperan en la barrera del lavamanos. El servicio empieza cuando pulsas
**Abrir servicio** *y* todos terminaron de lavarse.

### 3. Mantén la despensa llena

Cada receta gasta ingredientes:

| Receta | Ingredientes | Pasos | Precio |
|---|---|---|---|
| Sopa | Tomate, Cebolla | Tabla → Estufa | $8 |
| Hamburguesa | Carne, Pan, Cebolla | Tabla → Estufa | $14 |
| Pizza | Masa, Queso, Tomate | Tabla → Horno | $16 |

Empiezas con $20 y 4 unidades de cada ingrediente. Con los botones de
**Despensa** compras 3 unidades de un ingrediente. Si un cocinero no encuentra
lo que necesita, pone cara de preocupación y vuelve a intentarlo hasta que
compres o se le acabe el tiempo al pedido.

### 4. ¿Cómo se gana y cómo se pierde dinero?

- Cada cliente espera **35 segundos**. Si el plato llega a tiempo, cobras el
  precio completo; si llega tarde, cobras la mitad.
- Un pedido perdido (el cliente se fue, faltaron ingredientes o nadie lo
  atendió antes del cierre) te cuesta **$3** de multa.
- Puede haber hasta 6 pedidos pendientes a la vez.

Al final de cada servicio verás un resumen, y al final de la jornada el dinero
total, los pedidos entregados y perdidos, y las violaciones de concurrencia.

### 5. Observa a los hilos

Cada avatar se anima según lo que está haciendo su hilo:

- camina entre zonas
- se lava las manos con burbujas
- bosteza esperando en la barrera
- se preocupa cuando faltan ingredientes
- espera impaciente en la cola de una estación
- pica en la tabla, revuelve en la estufa y mete la pizza al horno
- sonríe al entregar

El **Panel de concurrencia** muestra en vivo el estado de cada semáforo, lock,
barrera y Event.

## ¿Cómo jugar con sincronización y sin ella?

La casilla **Modo SIN sincronización (ver errores)** del panel cambia la forma
en que los cocineros usan los recursos compartidos. Se puede marcar y desmarcar
en cualquier momento de la partida.

### Modo sincronizado (por defecto)

Es el juego "correcto":

- **Estaciones con semáforo.** Una estación nunca tiene más cocineros que
  puestos: 2 tablas, 2 estufas y 1 horno. Los demás esperan en la cola, debajo
  de la estación. En el panel, `contador sem` baja cuando alguien entra y sube
  cuando sale.
- **Despensa con lock.** Comprobar si hay ingredientes y sacarlos es una sola
  operación. El panel muestra quién tiene el lock en cada momento, y el stock
  nunca baja de cero.
- **Violaciones: 0.** Si todo funciona, este contador se queda en cero toda la
  partida.

Aquí el reto es de gestión: decide qué comprar y cuándo, para que los
cocineros no se queden esperando ingredientes mientras los pedidos vencen.

### Modo SIN sincronización

Sirve para ver qué se rompe cuando se quitan los semáforos y los locks. Los
cocineros usan la estrategia ingenua *comprobar y luego actuar*
(check-then-act), con una pausa de medio segundo entre las dos cosas:

- **Sobrecupo en las estaciones.** Un cocinero ve un puesto libre, camina hacia
  él… y otro llega primero. Aparece la franja roja **¡SOBRECUPO!**, el
  contador "libres" se vuelve negativo y el semáforo ni se entera: su contador
  no cambia, porque nadie lo usa.
- **Ingredientes negativos.** Dos cocineros ven el mismo último tomate y los dos
  lo toman. El stock se pinta de rojo con números negativos.
- **Violaciones > 0.** El panel se pone en rojo y cuenta cada error de
  concurrencia.

Para provocar errores rápido:

- Deja que lleguen varias **pizzas**: el horno tiene un solo puesto, así que es
  fácil que dos cocineros lo ocupen a la vez.
- Deja que un ingrediente baje a 1 o 2 unidades y espera a que dos cocineros
  lo busquen al mismo tiempo.

La **caja registradora** siempre usa su lock, en los dos modos, para que el
marcador de dinero sea confiable. Al volver al modo sincronizado, los nuevos
accesos vuelven a ser seguros, pero las violaciones que ya ocurrieron quedan
contadas.

## ¿Qué necesito para jugar?

| Requisito | Detalle |
|---|---|
| **Python** | 3.8 o superior. |
| **Tkinter** | Viene con Python, pero algunas instalaciones no lo traen (ver abajo). |
| **Tk** | Versión **8.6 o superior**. En macOS reciente, Tk 8.5 muestra la ventana en blanco. |
| **Librerías extra** | Ninguna. Los avatares se dibujan solo con Tkinter. |

Para revisar tu Python:

```bash
python3 --version
python3 -c "import tkinter; print('Tk', tkinter.TkVersion)"
```

Debe decir Python 3.8 o más y Tk 8.6 o más. Si sale
`ModuleNotFoundError: No module named '_tkinter'`, a ese Python le falta Tk.

### ¿Cómo consigo un Python que sirva?

- **macOS:** el Python de Apple (`/usr/bin/python3`, el de Command Line Tools)
  trae Tk 8.5 y **no sirve**. Usa uno de estos:
  - el instalador de [python.org](https://www.python.org/downloads/)
  - Anaconda
  - Homebrew, instalando también Tk: `brew install python-tk@3.x` (cambia `3.x`
    por tu versión, por ejemplo `python-tk@3.14`)
- **Windows:** el instalador de python.org incluye Tkinter si dejas marcada la
  opción *tcl/tk and IDLE*.
- **Linux:** instala el paquete de Tk de tu distribución, por ejemplo
  `sudo apt install python3-tk` en Ubuntu o Debian.

## ¿Cómo lo ejecuto?

Desde la carpeta del proyecto:

```bash
python3 cocina_concurrente.py
# o bien
python3 -m cocina
```

Si tienes varios Python instalados, usa la ruta completa del que tenga Tk 8.6,
por ejemplo:

```bash
/opt/anaconda3/bin/python3 cocina_concurrente.py
```

Pruebas automáticas (no abren ventanas):

```bash
python3 -m unittest discover -s tests -t .
```

Los valores del juego (duración, precios, recetas, cocineros…) están en
[`cocina/config.py`](cocina/config.py).

## ¿Dónde está cada concepto del curso?

| Concepto | Dónde |
|---|---|
| **HILOS** | Cada cocinero ([`juego/cocinero.py`](cocina/juego/cocinero.py)), el jefe ([`juego/jefe.py`](cocina/juego/jefe.py)) y el generador de pedidos ([`juego/generador.py`](cocina/juego/generador.py)). Se lanzan en `Juego.iniciar` ([`juego/juego.py`](cocina/juego/juego.py)). La interfaz es el hilo principal. |
| **SEMÁFOROS** | Las estaciones ([`dominio/estacion.py`](cocina/dominio/estacion.py)): 2 tablas de picar, 2 estufas y 1 horno. Varios cocineros pueden usar una estación a la vez, pero nunca más de los puestos que tiene. |
| **LOCKS** | La despensa ([`dominio/despensa.py`](cocina/dominio/despensa.py)): comprobar y descontar ingredientes debe ser una sola operación. La caja registradora ([`dominio/caja.py`](cocina/dominio/caja.py)). `LockVisible` ([`concurrencia/lock_visible.py`](cocina/concurrencia/lock_visible.py)) recuerda quién lo tiene. |
| **BARRERAS** | [`concurrencia/control_servicio.py`](cocina/concurrencia/control_servicio.py). Al inicio de cada servicio nadie empieza hasta que todos se laven las manos y el jefe abra; al cierre, nadie cuenta el dinero hasta que todos terminen el plato que tenían. |
| **Event** | Servicio abierto/cerrado y orden de abrir, en `ControlServicio`. |
| **queue.Queue** | Pedidos por preparar ([`dominio/tablero.py`](cocina/dominio/tablero.py)) y mensajes hacia la interfaz ([`eventos.py`](cocina/eventos.py)). |
| **Con y sin sincronización** | [`concurrencia/sincronizacion.py`](cocina/concurrencia/sincronizacion.py): la versión correcta y la ingenua (check-then-act) de cada acceso, lado a lado. |

## ¿Cómo está organizado el código?

```
cocina_concurrente.py        punto de entrada
cocina/
  config.py                  Configuracion (valores del juego)
  eventos.py                 mensajes de los hilos hacia la interfaz
  main.py / __main__.py      arranque
  dominio/                   receta, pedido, actividad, destinos, estación,
                             despensa, caja, tablero
  concurrencia/              LockVisible, modos de sincronización, ControlServicio
  juego/                     Cocinero, Jefe, GeneradorPedidos, Mostrador, Compras,
                             FotoJuego y Juego (arma todas las piezas)
  ui/                        tema, layout, VistaCocina (lienzo), PanelControl, App,
                             PantallaInicio y validación de nombres
  ui/avatar/                 apariencia (opciones), poses (animaciones), dibujo
tests/                       pruebas con unittest
```

## ¿Cómo funcionan las animaciones?

1. Cada cocinero (hilo) publica, junto con su texto de estado, una
   `Actividad` ([`dominio/actividad.py`](cocina/dominio/actividad.py)): lavando,
   en la barrera, cocinando en tal estación, entregando…
2. La interfaz convierte esa actividad en una **pose**
   ([`ui/avatar/poses.py`](cocina/ui/avatar/poses.py)). Una pose dice dónde van
   los pies y las manos, qué cara pone, qué herramienta tiene en la mano y qué
   efectos lo rodean. Mientras el avatar se desplaza, usa la pose de caminar.
3. [`ui/avatar/dibujo.py`](cocina/ui/avatar/dibujo.py) dibuja la pose con formas
   del Canvas, sin imágenes ni librerías extra.

¿Quieres agregar un peinado, accesorio, cara, herramienta o efecto? Escribe su
función y regístrala en la tabla correspondiente de `dibujo.py` (y, si se puede
elegir en la pantalla de inicio, también en `apariencia.py`). Para animar una
estación nueva, registra su acción en `ACCIONES_ESTACION` (`poses.py`) y su
aparato en `APARATOS` ([`ui/vista_cocina.py`](cocina/ui/vista_cocina.py)).
