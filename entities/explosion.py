import pyglet
import os
from random import randint
from Scheduler import scheduler
class explosion(pyglet.sprite.Sprite):
    def __init__(self, explosion_img, x, y, batch, Scheduler: scheduler):
        super().__init__(explosion_img, x=x, y=y, batch=batch)
        self.batch = batch
        # Ensure you have an explosion image at the given path.
        self.scale = 5
        self.rotation = randint(0,360)
        Scheduler.schedule_update(setattr, 6, (self, 'active', False))
        self.active = True
