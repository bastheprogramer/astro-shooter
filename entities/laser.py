import pyglet
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import GameWindow

class laser(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, rotation, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = 600
        self.active = True
        
        # Calculate velocity once upon creation
        rads = math.radians(rotation)
        self.vel_x = math.sin(rads) * self.speed
        self.vel_y = math.cos(rads) * self.speed

    def update(self, dt, game: "GameWindow"):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Bounds check
        if self.x < 0 or self.x > game.width or self.y < 0 or self.y > game.height:
            self.active = False

