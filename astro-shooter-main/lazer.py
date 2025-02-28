import pyglet
from pyglet.image import load
from pyglet.sprite import Sprite
from numba import njit
from numpy import radians, sin,cos
@njit
def set_speed(R):
    x_speed = sin(radians(R)) * 600
    y_speed = cos(radians(R)) * 600
    return x_speed,y_speed
class Lazer:

    def __init__(self, X, Y, R, batch,lazer_img):
        self.lazer_sprite = Sprite(lazer_img, batch=batch)

        self.lazer_sprite.x = X
        self.lazer_sprite.y = Y
        self.lazer_sprite.rotation = R
        self.x_speed ,self.y_speed = set_speed(R)
        self.RNT = False

    def update(self, dt):
        self.lazer_sprite.x += self.x_speed * dt
        self.lazer_sprite.y += self.y_speed * dt

    def is_out_of_bounds(self, width=800, height=600):
        """Return True if the laser is outside the game boundaries."""
        return (self.lazer_sprite.x < 0 or self.lazer_sprite.x > width or
                self.lazer_sprite.y < 0 or self.lazer_sprite.y > height)

    def collides_with(self, astroid):
        return (
            abs(self.lazer_sprite.x - astroid.astrode_sprite.x) < 60
            and abs(self.lazer_sprite.y - astroid.astrode_sprite.y) < 30
        )
