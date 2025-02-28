import pyglet
from pyglet.image import load
from pyglet.sprite import Sprite
import random
from numba import njit
from numpy import radians, sin,cos,sqrt
@njit
def set_speed(R,M):
    x_speed = sin(radians(R)) * M
    y_speed = cos(radians(R)) * M
    return x_speed,y_speed

class astrode:
    def __init__(self, batch, x, y, x_speed, y_speed, rotation, RS, size, astrode_img, type_val=3):
        self.batch = batch
        self.astrode_img = astrode_img
        self.astrode_sprite = Sprite(astrode_img, batch=batch)
        self.astrode_sprite.x = x
        self.astrode_sprite.y = y
        self.astrode_sprite.scale = size
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.astrode_sprite.rotation = rotation
        self.RS = RS
        self.type = type_val

    def update(self, dt):
        self.astrode_sprite.x += self.x_speed * dt
        self.astrode_sprite.y += self.y_speed * dt
        self.astrode_sprite.rotation += self.RS * dt

    def is_out_of_bounds(self, width=800, height=600):
        return (self.astrode_sprite.x < 0 or self.astrode_sprite.x > width or
                self.astrode_sprite.y < 0 or self.astrode_sprite.y > height)

    def explode(self):
        fragments = []
        if self.type > 1:
            num_fragments = random.randint(2, 4)
            for i in range(num_fragments):
                angle_variation = random.uniform(-90, 90)
                new_rotation = self.astrode_sprite.rotation + angle_variation
                speed = sqrt(self.x_speed**2 + self.y_speed**2)
                speed *= random.uniform(1, 2)
                new_speed_x,new_speed_y = set_speed(new_rotation,speed)
                new_size = self.astrode_sprite.scale * 0.6
                new_RS = self.RS + random.uniform(-10, 10)
                fragment = astrode(
                    self.batch,
                    x=self.astrode_sprite.x,
                    y=self.astrode_sprite.y,
                    x_speed=new_speed_x,
                    y_speed=new_speed_y,
                    rotation=new_rotation,
                    RS=new_RS,
                    size=new_size,
                    type_val=self.type - 1,
                    astrode_img=self.astrode_img
                )
                fragments.append(fragment)
        return fragments
