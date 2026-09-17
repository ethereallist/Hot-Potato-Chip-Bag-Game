# Changelog

Todos los cambios notables de **Hot Potato Chip Bag** se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Diagrama de clases inicial: `PlayState`, `MenuState`, `WinState`.
- Subestados de `PlayState`: `ConstructionState`, `ScoreState`, `ParkourState`.
- Clase `Player` con flags de intención, posición, velocidad y estado de papa caliente.
- Clase `Consumible` para powerups temporales.
- Clase `Mapa` con dos capas y casillas manipulables (suelo, hueco, pared).

### Changed

### Deprecated

### Removed

### Fixed

### Security

<!--
## [0.1.0] - YYYY-MM-DD

### Added
- Primer prototipo jugable con 4 jugadores locales.

[Unreleased]: https://github.com/usuario/hot-potato-chip-bag/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/usuario/hot-potato-chip-bag/releases/tag/v0.1.0
-->

## V0.1.0 -2026/09/16

### Added

- Personaje jugable "personapa".
- Se puede mover.
- Puede hacer dash con sistema de partículas.
- Puede colisionar con otros objetos o personapas.

## [0.5.0] - 2026-09-17

### Added

Map

## [0.6.0] - 2026-09-17

### Added

PlayState


## [0.7.0] - 2026-09-17

### Added
- Control del jugador 3 con mando, leído directamente con `pygame.joystick` (sondeo por frame) en vez de por el sistema de eventos de Gale — más confiable para el hardware que estábamos probando.
- Opción para invertir el eje vertical del stick (`invert_y`), ya que distintos mandos reportan la dirección "arriba" al revés.

### Fixed
- `PlayerController`: las líneas que leían `axis_x`/`axis_y` estaban fuera del bloque que filtra por tipo de dispositivo — un jugador de teclado terminaba reaccionando también al stick de un mando conectado. Ya quedan correctamente aisladas dentro del bloque de `device == "gamepad"`.
- Se eliminaron las clases de comando sin usar (`MoveLeftCommand`, `MoveRightCommand`, `MoveUpCommand`, `MoveDownCommand` con `move_*_intent`) que quedaron de una versión anterior y nunca se llegaron a bindear.

## [0.7.1] - 2026-09-17

### Fixed
- Se arregló la colision con las paredes, el collidebox del jugador ahora se obtiene con getrect.