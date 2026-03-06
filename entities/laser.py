import math
from typing import TYPE_CHECKING

from entities.gameobject import gameobject

if TYPE_CHECKING:
    from main import GameWindow


class laser(gameobject):
    def __init__(self, img, x, y, rotation, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = 600

        # Calculate velocity once upon creation
        rads = math.radians(rotation)
        self.vel_x = math.sin(rads) * self.speed
        self.vel_y = math.cos(rads) * self.speed

    def update(self, dt, game: "GameWindow"):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        if self.is_out_of_bounds(game.width, game.height):
            self.deactivate()
