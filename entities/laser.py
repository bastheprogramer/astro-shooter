import pyglet
import math

class Laser(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, rotation, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = 600
        self.active = True
        
        # Calculate velocity once upon creation
        rads = math.radians(rotation)
        self.vel_x = math.sin(rads) * self.speed
        self.vel_y = math.cos(rads) * self.speed

    def update(self, dt, width, height):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Bounds check
        if self.x < 0 or self.x > width or self.y < 0 or self.y > height:
            self.active = False

