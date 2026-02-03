import pyglet
import os
from random import randint
class Explosion:
    def __init__(self, x, y, batch,explosion_img):
        self.batch = batch
        # Ensure you have an explosion image at the given path.
        self.sprite = pyglet.sprite.Sprite(
            explosion_img, x=x, y=y, batch=batch)
        self.sprite.scale = 5
        self.sprite.rotation = randint(0,360)
        self.lifetime = 0.1  # Explosion lasts 0.5 seconds.
        self.elapsed = 0

    def update(self, dt):
        self.elapsed += dt
        # Optionally add fade-out effect by modifying sprite.opacity here.
        if self.elapsed >= self.lifetime:
            return False  # Explosion finished.
        return True
