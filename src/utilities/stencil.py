"""Cropper: clase de utilidad para recortar imagenes 
o generar texturas de color plano a partir de una forma ."""

import pygame
import settings
from gale.stencil import Stencil

class Cropper:
    @staticmethod
    def print_shape(
        shape: pygame.Surface,
        color: tuple[int,int,int] = (255,255,255)
    ) -> pygame.Surface:
        size = shape.get_size()
        temp = Stencil(size)
        temp.draw(lambda mask: mask.blit(shape, (0,0)))
        flat_color = pygame.Surface(size, pygame.SRCALPHA)
        flat_color.fill(color)
        temp.apply(flat_color)
        return flat_color
    
    @staticmethod    
    def crop_shape(
        image: pygame.Surface,
        shape: pygame.Surface,
        pos: tuple[int,int] = (0,0)
    ) -> pygame.Surface:
        img = image.convert_alpha()
        size = image.get_size()
        temp = Stencil(size)
        temp.draw(lambda mask: mask.blit(shape, pos))
        temp.apply(img)
        return img