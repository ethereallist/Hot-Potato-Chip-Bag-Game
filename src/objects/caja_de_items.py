"""CajaDeItems: caja central con los objetos disponibles para tomar
durante ConstructionState."""


class CajaDeItems:
    def __init__(self) -> None:
        self.duracion: float = 0.0
        self.objetos = []  # list[Objeto]

    def remove_item(self, obj) -> None:
        pass
