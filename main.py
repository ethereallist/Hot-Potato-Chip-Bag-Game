"""Punto de entrada de Hot Potato Chip Bag.

Sigue el mismo patrón que los proyectos de gale-admin create-project:
un main.py mínimo que solo instancia el Game y lo ejecuta.
"""

from src.game import HotPotatoChipBagGame


if __name__ == "__main__":
    HotPotatoChipBagGame(title="Hot Potato Chip Bag").exec()
