import pyglet
import random
import math

class PowerUp(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch, ptype=None):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = 0.15
        self.active = True
        self.y_speed = -100  # Falls downward
        
        # If no type is specified, pick a random one
        if ptype:
            self.ptype = ptype
        else:
            # Weighted choice (life is rare, fastfire is common, score is very common)
            self.ptype = random.choices(
                ["life", "score", "speed", "fastfire"],
                weights=[10, 50, 20, 30], 
                k=1
            )[0]

    def update(self, dt):
        """Moves the powerup and checks bounds."""
        self.y += self.y_speed * dt
        
        # Deactivate if it falls off the bottom of the screen
        if self.y < -50:
            self.active = False

    def apply(self):
        """
        Returns the type of powerup. 
        The Game class calls this upon collision to determine what to do.
        """
        self.active = False
        return self.ptype