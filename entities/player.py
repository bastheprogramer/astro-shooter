import pyglet
import math
from pyglet.window import key

class Player(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = 0.1
        self.velocity_x = 0
        self.velocity_y = 0
        self.drag = 0.95  # Physics drag
        self.accel = 20.0 # Acceleration speed

    def update(self, dt, keys, mouse_x, mouse_y):
        # 1. Rotation (Point to mouse)
        dx = self.x - mouse_x
        dy = self.y - mouse_y
        target_angle = -math.degrees(math.atan2(dy, dx)) - 90
        self.rotation = target_angle

        # 2. Movement (WSAD)
        # We add acceleration to velocity, rather than setting position directly
        if keys[key.W]: self.velocity_y += self.accel
        if keys[key.S]: self.velocity_y -= self.accel
        if keys[key.A]: self.velocity_x -= self.accel
        if keys[key.D]: self.velocity_x += self.accel

        # 3. Apply Physics
        self.velocity_x *= self.drag
        self.velocity_y *= self.drag
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt