from random import randint

from Scheduler import scheduler
from entities.GameObject import GameObject


class Explosion(GameObject):
    def __init__(self, explosion_img, x, y, batch, Scheduler: scheduler):
        super().__init__(explosion_img, x=x, y=y, batch=batch)
        self.scale = 5
        self.rotation = randint(0, 360)
        Scheduler.schedule_update(setattr, 6, (self, 'active', False))
