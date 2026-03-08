import math
import pyglet

from entities.GameObject import GameObject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import GameWindow

class Player(GameObject):
    def __init__(self, img, x, y, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = 0.1
        self.velocity_x = 0
        self.velocity_y = 0
        self.drag = 0.95  # Physics drag
        self.accel = 20.0  # Acceleration speed
        self.is_vulnerable = True

    def apply_drag(self):
        self.velocity_x *= self.drag
        self.velocity_y *= self.drag

    def update(self, dt, game: "GameWindow"):
        # 1. Rotation (Smooth LERP to mouse)
        dx = game.mouse_x - self.x
        dy = game.mouse_y - self.y

        # Calculate target angle (Pyglet uses clockwise degrees)
        target_angle = -math.degrees(math.atan2(dy, dx)) + 90

        # Calculate the shortest distance between current and target angle (-180 to 180)
        angle_diff = (target_angle - self.rotation + 180) % 360 - 180

        # LERP Factor: Higher number = snappier, Lower number = "floatier"
        turn_speed = 15.0

        # Ease the rotation towards the target
        self.rotation += angle_diff * (turn_speed * dt)
        self.rotation %= 360

        # 2. Movement (WASD)
        if game.keys[pyglet.window.key.W]:
            self.velocity_y += self.accel
        if game.keys[pyglet.window.key.S]:
            self.velocity_y -= self.accel
        if game.keys[pyglet.window.key.A]:
            self.velocity_x -= self.accel
        if game.keys[pyglet.window.key.D]:
            self.velocity_x += self.accel

        self.apply_drag()

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        self.x = max(20, min(game.width-20, self.x))
        self.y = max(20, min(game.height-20, self.y))