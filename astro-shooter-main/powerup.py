import pyglet
import math
import random

class PowerUp:
    def __init__(self, x, y, batch,powerup_img, ptype=None):
        self.batch = batch
        self.sprite = pyglet.sprite.Sprite(
            powerup_img, x=x, y=y, batch=batch)
        self.sprite.scale = 0.15
        self.x_speed = 0
        self.y_speed = -100  # Falls downward.
        self.active = True
        # Choose a power-up type: "life", "score", "speed", "tryL", or "shield".
        self.ptype = ptype if ptype is not None else random.choice(["life", "score", "speed", "tryL", "shield"])
    
    def update(self, dt):
        self.sprite.x += self.x_speed * dt
        self.sprite.y += self.y_speed * dt
        if self.sprite.y < 0:
            self.active = False

    def collides_with(self, player_sprite):
        dx = self.sprite.x - player_sprite.x
        dy = self.sprite.y - player_sprite.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < 60

    def apply(self):
        effect = {}
        if self.ptype == "life":
            effect["lives"] = 1
        elif self.ptype == "score":
            effect["score"] = 2500
        elif self.ptype == "speed":
            effect["speed_boost"] = 2.0
            effect["speed_duration"] = 5.0
        elif self.ptype == "tryL":
            effect["tryL"] = True
            effect["tryL_duration"] = 5.0
        elif self.ptype == "shield":
            effect["shield"] = True
            effect["shield_duration"] = 5.0
        self.active = False

        return effect
