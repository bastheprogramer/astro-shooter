import pyglet
import os

sprites_dir = os.path.join(os.path.dirname(__file__), 'sprites')
explosion_img = pyglet.image.load(os.path.join(sprites_dir,"explosion.png"))
explosion_img.anchor_x = explosion_img.width // 2
explosion_img.anchor_y = explosion_img.height // 2
class Explosion:
    def __init__(self, x, y, batch):
        global explosion_img
        self.batch = batch
        # Ensure you have an explosion image at the given path.
        self.sprite = pyglet.sprite.Sprite(
            explosion_img, x=x, y=y, batch=batch)
        self.sprite.scale = 5
        self.lifetime = 0.1  # Explosion lasts 0.5 seconds.
        self.elapsed = 0

    def update(self, dt):
        self.elapsed += dt
        # Optionally add fade-out effect by modifying sprite.opacity here.
        if self.elapsed >= self.lifetime:
            return False  # Explosion finished.
        return True
