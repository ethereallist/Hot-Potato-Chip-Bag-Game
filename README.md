# 🥔🔥 Hot Potato Chip Bag

Juego couch multijugador para 4 jugadores hecho en **Python** con **Pygame** y **Gale**.

Cada jugador es una papa. En cada ronda, una papa es elegida al azar como la **papa caliente**:
tienes que empujar a los demás jugadores para pasarles el turno antes de que la papa te
explote encima. Entre ronda y ronda, los propios jugadores rediseñan el mapa colocando,
rotando y moviendo casillas antes de volver a jugar.

<!-- GIF o screenshot del gameplay aquí -->

---

## Índice

- [Concepto](#concepto)
- [Controles](#controles)
- [Requisitos e instalación](#requisitos-e-instalación)
- [Cómo correr el juego](#cómo-correr-el-juego)
- [Solución de problemas](#solución-de-problemas)
- [Flujo de una partida](#flujo-de-una-partida)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Roadmap](#roadmap)
- [Créditos](#créditos)
- [Licencia](#licencia)

---

## Concepto

- Partida para **4 jugadores** en el mismo control/pantalla (couch multiplayer).
- La partida dura **3 rondas**.
- Pierde el jugador que se queda sin puntos.
- Cada ronda alterna entre tres fases:
  1. **Construcción**: los jugadores modifican el mapa (mover, rotar y colocar casillas).
  2. **Parkour**: los jugadores se mueven por el mapa y se empujan para pasarse la papa caliente antes de que explote.
  3. **Puntaje**: se reparten/restan puntos según cómo terminó la ronda y se decide si el juego continúa o hay un ganador.

## Controles

Cada jugador tiene una **acción principal** (hacer *dash* en el parkour, mover el cursor/confirmar en
los menús y en la construcción) y una **acción secundaria** (¡gritar!).

| Acción              | Jugador 1 (teclado) | Jugador 2 (teclado)     | Jugador 3 (mando)                    | Jugador 4 |
| ------------------- | ------------------- | ----------------------- | ------------------------------------ | --------- |
| **Mover**           | `W` `A` `S` `D`     | Flechas `←` `↑` `↓` `→` | Stick izquierdo                      | *Pendiente* |
| **Dash**            | `E`                 | `Espacio`               | Botón `A` / `✕` (botón 0)            | *Pendiente* |
| **Acción / cursor** | `E`                 | `Espacio`               | Botón `A` / `✕` (botón 0)            | *Pendiente* |
| **Gritar**          | `Q`                 | `Enter`                 | Botón `B` / `○` (botón 1)            | *Pendiente* |
| **Confirmar**       | `E`                 | `Espacio`               | Botón `A` / `✕` (botón 0)            | *Pendiente* |

- **Dash, Acción / cursor y Confirmar** son la misma tecla: la **acción principal** de cada jugador.
- **Gritar** es la **acción secundaria**. Al empezar cada partida se reparte un grito distinto a cada jugador
  (hay 13 sonidos, así que van rotando de una partida a otra). Solo suena al presionar el botón, no mientras
  lo mantienes.
- **Menú principal:** `W` / `S` para elegir y `E` para confirmar (controles del jugador 1).
- **Elegir sombrero:** los jugadores eligen por turnos con `W` `A` `S` `D` y confirman con `E`.
- **Pantalla de victoria:** cualquier jugador puede moverse entre las opciones y confirmar con su acción principal.
- El jugador 3 usa el **primer mando** que detecte el sistema (la numeración de los botones puede variar según
  el modelo de mando; ver [Probar tus mandos](#probar-tus-mandos)).
- El jugador 4 todavía no tiene dispositivo asignado en el parkour (falta un segundo mando). Sus teclas
  (`F` `H` `T` `G` + `Y` / `R`) y las del jugador 3 en teclado (`J` `L` `I` `K` + `P` / `O`) ya están definidas
  en `settings.py`, reservadas para más adelante.

## Requisitos e instalación

No hay nada que compilar: el proyecto es Python puro y todas sus dependencias se instalan con `pip`.

### Qué necesitas

| Requisito | Detalle |
| --------- | ------- |
| **Python** | 3.9 o superior. Recomendado **3.12** (con el que se ha probado). |
| **Git** | Para clonar el repositorio (o descarga el ZIP desde GitHub). |
| **Gale** | Se instala solo con `pip` (paquete [`gale-engine`](https://pypi.org/project/gale-engine/)). |
| **Pygame** | Se instala solo junto con Gale, no hace falta instalarlo aparte. |
| **Teclado + un mando** | Para jugar con 3 personas hoy: 2 en teclado y 1 con mando. El mando es opcional para probar. |

Las dependencias que instala `requirements.txt` son:

- [`gale-engine`](https://pypi.org/project/gale-engine/): el motor sobre el que está hecho el juego (estados, temporizadores, entradas, etc.).
- [`pygame`](https://pypi.org/project/pygame/): ventana, gráficos, audio y mandos.
- Gale, a su vez, trae `numpy`, `pymunk` y `click`.

### Paso a paso (con entorno virtual)

Un **entorno virtual (`venv`)** mantiene las dependencias del juego aisladas del resto de tu computador.
Solo se crea una vez; después basta con activarlo cada vez que abras una terminal nueva.

**1. Clona el repositorio**

```bash
git clone https://github.com/ethereallist/Hot-Potato-Chip-Bag-Game.git
cd Hot-Potato-Chip-Bag-Game
```

**2. Crea el entorno virtual** (dentro de la carpeta del proyecto)

```bash
# macOS / Linux
python3 -m venv .venv

# Windows
py -m venv .venv
```

**3. Actívalo**

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat
```

Sabrás que funcionó porque la terminal mostrará `(.venv)` al inicio de la línea.

**4. Instala las dependencias**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**5. (Opcional) Comprueba la instalación**

```bash
python -c "import gale, pygame; print('Todo listo, pygame', pygame.version.ver)"
```

## Cómo correr el juego

Con el entorno virtual **activado** y parado en la **carpeta raíz del proyecto** (donde está `main.py`):

```bash
python main.py
```

Se abre una ventana de 700 × 500. Cuando termines, cierra la ventana y, si quieres salir del
entorno virtual, escribe `deactivate`.

Las siguientes veces solo necesitas dos comandos:

```bash
cd Hot-Potato-Chip-Bag-Game
source .venv/bin/activate        # en Windows: .venv\Scripts\Activate.ps1
python main.py
```

> 💡 `settings.py` tiene que quedarse en la raíz, junto a `main.py`: Gale lo lee automáticamente
> para configurar la ventana y los controles.

### Probar tus mandos

Si tu mando no responde como esperas, conéctalo y corre:

```bash
python test_game.py
```

Se abre una ventanita de prueba y, en la consola, aparece cada mando detectado junto con el ID de cada
botón y de cada eje que vayas moviendo. Sirve para comprobar qué números usa tu mando.

## Solución de problemas

| Problema | Solución |
| -------- | -------- |
| `error: externally-managed-environment` al hacer `pip install` | El entorno virtual **no está activado**. Actívalo (paso 3) y verifica que aparezca `(.venv)` en la terminal. |
| `ModuleNotFoundError: No module named 'gale'` (o `'pygame'`) | Estás usando un Python distinto al del entorno virtual. Activa el `venv` y usa `python -m pip install -r requirements.txt`. |
| `pygame.error: No file 'assets/sounds/lobby.mp3' found in working directory …` | Corriste el juego desde otra carpeta. Haz `cd` a la raíz del proyecto (donde está `main.py`) y vuelve a correr `python main.py`. |
| `python: command not found` | En macOS/Linux usa `python3`; en Windows usa `py`. Dentro del entorno virtual activado, `python` ya funciona. |
| `ensurepip is not available` al crear el venv (Ubuntu/Debian) | Instala el módulo: `sudo apt install python3-venv`. |
| PowerShell: *"la ejecución de scripts está deshabilitada"* | Ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activar el venv (solo afecta a esa ventana de terminal). |
| `pip` intenta compilar pygame y falla | Suele pasar con versiones de Python muy nuevas que aún no tienen paquetes precompilados de pygame. Usa Python 3.12. |
| Un mando no es reconocido en macOS | Descarga [`gamecontrollerdb.txt`](https://github.com/mdqinc/SDL_GameControllerDB) y colócalo en la raíz del proyecto; `settings.py` lo carga automáticamente si existe. |
| El jugador 3 no se mueve | Es lo esperado si no hay ningún mando conectado. Conéctalo *antes* de abrir el juego. |

## Flujo de una partida

```
MenuState             (JUGAR / SALIR → cada jugador elige su sombrero)
   │
   ▼
PlayState
   │
   ├── ParkourState  (se mueven y se pasan la papa caliente)
   │        │
   │        ▼
   ├── ScoreState    (se actualizan y muestran los puntos)
   │        │
   │        ├──► siguiente ronda → vuelve a ParkourState
   │        │
   │        └──► fin de la partida → WinState
   │
   └── ConstructionState  (se rediseña el mapa entre rondas; en desarrollo, aún no está conectado)

WinState              (ganador, confeti y opciones: VOLVER A JUGAR / IR AL MENÚ)
```

Cada estado (`PlayState`, `MenuState`, `WinState`) corre con su propio temporizador.

## Arquitectura del proyecto

```
Hot-Potato-Chip-Bag-Game/
├── main.py                       # Punto de entrada
├── settings.py                   # Ventana, controles, texturas y sonidos (lo lee Gale)
├── requirements.txt
├── test_game.py                  # Script para probar mandos
├── CHANGELOG.md
├── assets/
│   ├── fonts/
│   ├── images/
│   ├── sounds/
│   └── sprites/                  # Personapas y sombreros
└── src/
    ├── game.py                   # Game de Gale y registro de estados
    ├── states/
    │   ├── menu_state.py
    │   ├── play_state.py
    │   ├── win_state.py
    │   ├── map/
    │   │   └── map.py            # Grilla de casillas: suelo, hueco, pared
    │   └── play/
    │       ├── parkour_state.py
    │       ├── score_state.py
    │       └── construction_state.py
    ├── objects/
    │   ├── personapa.py          # Jugador: posición, velocidad, flags de intención, es_la_papa
    │   ├── personapa_sprite_renderer.py
    │   ├── hat_sprites.py        # Sombreros
    │   ├── sprite_animation.py
    │   ├── player_controller.py  # Teclado/mando → intenciones del jugador
    │   ├── gamepad_direct.py
    │   ├── cursor.py
    │   ├── object.py             # Piezas colocables del mapa
    │   ├── object_box.py
    │   ├── information_panel.py
    │   ├── podio.py
    │   ├── transitions.py        # Fundidos entre estados
    │   └── confetti.py           # Partículas de confeti
    └── utilities/
        ├── player_input_manager.py
        └── stencil.py
```

Para más detalle sobre las clases y relaciones entre ellas, ver el diagrama de clases
(`ARCHITECTURE.md` o link aquí cuando esté listo).

## Roadmap

El historial de cambios y versiones se documenta siguiendo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y [Semantic Versioning](https://semver.org/spec/v2.0.0.html) en [`CHANGELOG.md`](CHANGELOG.md).

Estado actual del proyecto: **prototipo jugable**.

- ✅ Menú con selección de sombreros, parkour con papa caliente y hundimiento progresivo del mapa, puntaje, podio y pantalla de victoria.
- 🚧 Fase de construcción del mapa (`ConstructionState`) por implementar.
- 🚧 Cuarto jugador (falta asignarle un segundo mando).

## Créditos

> ⚠️ Placeholder — agregar nombres/roles del equipo (diseño, programación, arte, etc.)

## Licencia

> ⚠️ Placeholder — definir licencia (ej. MIT, GPL-3.0) o marcar como "TBD".