import math
from typing import TYPE_CHECKING

from entities.WeaponObject import WeaponObject
if TYPE_CHECKING:
    from main import GameWindow


class Laser(WeaponObject):
    def __init__(self, img, x, y, rotation, batch):
        self.speed = 600
        super().__init__(img, x=x, y=y,rotation=rotation, batch=batch, speed=600)
        self.rotation = rotation
        

        # Calculate velocity once upon creation
        rads = math.radians(rotation)
        self.vel_x = math.sin(rads) * self.speed
        self.vel_y = math.cos(rads) * self.speed

    def update(self, dt, game: "GameWindow"):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        if self.is_out_of_bounds(game.width, game.height):
            self.deactivate()
