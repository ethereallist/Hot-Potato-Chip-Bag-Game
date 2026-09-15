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
- [Flujo de una partida](#flujo-de-una-partida)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Roadmap](#roadmap)
- [Créditos](#créditos)
- [Licencia](#licencia)

---

## Concepto

- Partida para **4 jugadores** en el mismo control/pantalla (couch multiplayer).
- La partida dura **3 × n rondas** (siendo *n* el número de jugadores).
- Pierde el jugador que se queda sin puntos.
- Cada ronda alterna entre tres fases:
  1. **Construcción**: los jugadores modifican el mapa (mover, rotar y colocar casillas).
  2. **Parkour**: los jugadores se mueven por el mapa y se empujan para pasarse la papa caliente antes de que explote.
  3. **Puntaje**: se reparten/restan puntos según cómo terminó la ronda y se decide si el juego continúa o hay un ganador.

## Controles

> ⚠️ Placeholder — completar con el mapeo real de botones/teclas por jugador.

| Acción              | Jugador 1 | Jugador 2 | Jugador 3 | Jugador 4 |
|---------------------|-----------|-----------|-----------|-----------|
| Mover               |           |           |           |           |
| Dash                |           |           |           |           |
| Acción / cursor     |           |           |           |           |
| Rotar objeto        |           |           |           |           |
| Confirmar           |           |           |           |           |

## Requisitos e instalación

> ⚠️ Placeholder — confirmar versión de Python, cómo se instala Gale (¿pip, submódulo, compilación propia?) y si hay más dependencias.

```bash
# Clonar el repositorio
git clone https://github.com/usuario/hot-potato-chip-bag.git
cd hot-potato-chip-bag

# Instalar dependencias
pip install -r requirements.txt
```

**Requisitos mínimos:**
- Python 3.x (especificar versión)
- Pygame
- Gale (especificar cómo se instala)
- Soporte para 4 controles físicos (o combinación teclado + mando)

## Cómo correr el juego

```bash
python main.py
```

## Flujo de una partida

```
MenuState
   │
   ▼
PlayState
   │
   ├── ParkourState  (se mueven y se pasan la papa caliente)
   │        │
   │        ▼
   ├── ScoreState    (se actualizan y muestran los puntos)
   │        │
   │        ▼
   └── ConstructionState  (se rediseña el mapa para la próxima ronda)
            │
            └──► vuelve a ParkourState (nueva ronda)

Cuando alguien gana o se llega al límite de rondas → WinState
```

Cada estado (`PlayState`, `MenuState`, `WinState`) corre con su propio temporizador.

## Arquitectura del proyecto

```
hot-potato-chip-bag/
├── main.py
├── states/
│   ├── menu_state.py
│   ├── play_state.py
│   ├── win_state.py
│   ├── parkour_state.py
│   ├── score_state.py
│   └── construction_state.py
├── objects/
│   ├── player.py          # Personapa: posición, velocidad, flags de intención, es_la_papa
│   ├── consumible.py       # Powerups temporales
│   ├── object.py           # Piezas colocables del mapa
│   └── cursor.py
├── map/
│   └── map.py             # Grilla de casillas: suelo, hueco, pared
├── assets/
└── requirements.txt
```

Para más detalle sobre las clases y relaciones entre ellas, ver el diagrama de clases
(`ARCHITECTURE.md` o link aquí cuando esté listo).

## Roadmap

El historial de cambios y versiones se documenta siguiendo
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) en [`CHANGELOG.md`](./CHANGELOG.md).

Estado actual del proyecto: **prototipo / en diseño** — arquitectura de estados y clases
principales en desarrollo.

## Créditos

> ⚠️ Placeholder — agregar nombres/roles del equipo (diseño, programación, arte, etc.)

## Licencia

> ⚠️ Placeholder — definir licencia (ej. MIT, GPL-3.0) o marcar como "TBD".
