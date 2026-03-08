import math
import random
from typing import TYPE_CHECKING

from entities.GameObject import GameObject

if TYPE_CHECKING:
    from main import GameWindow


class HostileObject(GameObject):
    """Base class for all hostile entities."""

    def __init__(self, img, x, y, batch, vel_x: float = 0, vel_y: float = 0):
        super().__init__(img, x=x, y=y, batch=batch)
        self.vel_x = vel_x
        self.vel_y = vel_y

    def update(self, dt: float, game: "GameWindow"):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        if self.is_out_of_bounds(game.width, game.height, margin=50):
            self.deactivate()
