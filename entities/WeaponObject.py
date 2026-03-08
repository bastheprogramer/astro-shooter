import math
import random
from typing import TYPE_CHECKING

from entities.GameObject import GameObject

if TYPE_CHECKING:
    from main import GameWindow


class WeaponObject(GameObject):
    """Base class for all player-fired projectiles."""

    def __init__(self, img, x, y, rotation: float, batch, speed: float):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = speed

    def update(self, dt: float, game: "GameWindow"):
        raise NotImplementedError
