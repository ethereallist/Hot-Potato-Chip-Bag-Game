# Changelog

Todos los cambios notables de **Hot Potato Chip Bag** se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Audio:** Integración de sonidos en los botones, el lobby, el estado de victoria (`WinState`) y el estado de parkour (`ParkourState`).
- **Estados de Juego:** Implementación funcional de los estados de Puntuación (`ScoreState`), Victoria (`WinState`) y adición del Podio.
- **Transiciones:** Lógica para transicionar fluidamente entre los estados de puntuación y parkour, complementada con clases de utilidad para transiciones visuales.
- **Interfaz y HUD:**
  - Barra de tiempo (*Time bar*) añadida.
  - Clase `Cursor` y utilidades de `Stencil` añadidas.
  - Animación de los jugadores moviéndose e interactuando en el menú principal.
- **Mapa:** Texturas y lógica para las casillas (*tiles*) del mapa integradas.
- **Parkour State:** Inserción de los personapas jugables y partículas de explosión dentro del estado de parkour.
- **Sistemas Base:** 
  - Clase `PlayerTracker` para el seguimiento estadístico de los jugadores.
  - Diagrama de clases inicial: `PlayState`, `MenuState`, `WinState`.
  - Subestados de `PlayState`: `ConstructionState`, `ScoreState`, `ParkourState`.
  - Clase `Player` con flags de intención, posición, velocidad y estado de papa caliente.
  - Clase `Consumible` para powerups temporales.
  - Clase `Mapa` con dos capas y casillas manipulables (suelo, hueco, pared).

### Changed
- **Animaciones:** La animación de la **papa caliente** se actualizó para utilizar el sistema `personapa_sprite_renderer`.
- **Animaciones:** Se mejoró a la calidad más alta la animación del ciclo de caminar (*walking cycle*) de los personajes.
- **Tipografía:** Se ajustaron las tipografías del menú principal.

### Deprecated

### Removed

### Fixed
- **Físicas y Colisiones:** Solucionado el problema de las paredes cayendo (*falling walls*).
- **Mecánicas:** Arreglados los problemas al pasar la papa caliente entre jugadores.
- **Visuales:** Corrección en la visualización de las partículas del *dash* en los personapas y reparación de un bug en la capa de datos visuales (`visual_data_layer`).
- **Mapa:** Arreglado el error que causaba que las casillas (*tiles*) se vieran hundidas o sin texturas cargadas.
- **Lógica de Juego:** 
  - Corrección del `ScoreState` para que funcione correctamente para todas las personapas.
  - Solucionado el problema con el seguimiento (*tracking*) de las rondas y puntuaciones globales.
  - Corrección en la lógica de los comandos del `PlayerController`.
  - Corrección menor añadiendo un argumento posicional faltante (*Added positional arg*).

### Security

<!--
## [0.1.0] - YYYY-MM-DD

### Added
- Primer prototipo jugable con 4 jugadores locales.

[Unreleased]: https://github.com/usuario/hot-potato-chip-bag/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/usuario/hot-potato-chip-bag/releases/tag/v0.1.0
-->

## V0.1.0 - 2026-09-16

### Added

- Personaje jugable "personapa".
- Se puede mover.
- Puede hacer dash con sistema de partículas.
- Puede colisionar con otros objetos o personapas.

## [0.5.0] - 2026-09-17

### Added

- Map

## [0.6.0] - 2026-09-17

### Added

- PlayState

## [0.7.0] - 2026-09-17

### Added
- Control del jugador 3 con mando, leído directamente con `pygame.joystick` (sondeo por frame) en vez de por el sistema de eventos de Gale — más confiable para el hardware que estábamos probando.
- Opción para invertir el eje vertical del stick (`invert_y`), ya que distintos mandos reportan la dirección "arriba" al revés.

### Fixed
- `PlayerController`: las líneas que leían `axis_x`/`axis_y` estaban fuera del bloque que filtra por tipo de dispositivo — un jugador de teclado terminaba reaccionando también al stick de un mando conectado. Ya quedan correctamente aisladas dentro del bloque de `device == "gamepad"`.
- Se eliminaron las clases de comando sin usar (`MoveLeftCommand`, `MoveRightCommand`, `MoveUpCommand`, `MoveDownCommand` con `move_*_intent`) que quedaron de una versión anterior y nunca se llegaron a bindear.

## [0.7.1] - 2026-09-17

### Fixed
- Se arregló la colisión con las paredes, el collidebox del jugador ahora se obtiene con getrect.

## [0.8.0] - 2026-09-17

### Added
- Menú principal con botones interactivos agregados, para moverse entre ellos se utiliza w, s y seleccionar con espacio.

## [0.9.0] - 2026-09-18

### Added

- Se añadió funcionalidad de selección de sombreros para cada personaje en el menú principal.