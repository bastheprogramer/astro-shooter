import pyglet
import random
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import GameWindow

class powerup(pyglet.sprite.Sprite):
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
                ["life", "score", "speed", "fastfire", "splitfire"],
                weights=[10, 50, 20, 30, 10], 
                k=1
            )[0]

    def update(self, dt):
        """Moves the powerup and checks bounds."""
        self.y += self.y_speed * dt
        
        # Deactivate if it falls off the bottom of the screen
        if self.y < -50:
            self.active = False

    def apply(self, game: "GameWindow"):
        """
        Returns the type of powerup. 
        The Game class calls this upon collision to determine what to do.
        """
        self.active = False
        # Apply powerup effects
        match self.ptype:
            case "life":
                game.lives += 1
            case "score":
                game.score += 500
            case "speed":
                game.player.accel = min(30, game.player.accel + 5)
            case "fastfire":
                game.fire_rate = 0.05  # Much faster shooting
                
                last_entry = game.Scheduler.cancel_schedule(self.stopfastfire)  # Cancel any existing reset tasks
                time = (last_entry[2] if last_entry else 0) + 10*60
                game.Scheduler.schedule_update(self.stopfastfire, time, (game,))  # Reset after 10 seconds  
            case "splitfire":
                game.split_fire = True
                
                last_entry = game.Scheduler.cancel_schedule(self.stopsplitfire)  # Cancel any existing reset tasks
                time = (last_entry[2] if last_entry else 0) + 10*60
                game.Scheduler.schedule_update(self.stopsplitfire, time, (game,))  # Reset after 10 seconds  
    @staticmethod
    def stopfastfire(game):
        """Temporarily increases fire rate."""
        game.fire_rate = 0.15

    @staticmethod
    def stopsplitfire(game):
        game.split_fire = False