import random
from typing import TYPE_CHECKING

from entities.GameObject import GameObject

if TYPE_CHECKING:
    from main import GameWindow


class PowerUp(GameObject):
    def __init__(self, img, x, y, batch, ptype=None):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = 0.15
        self.y_speed = -100  # Falls downward

        if ptype:
            self.ptype = ptype
        else:
            self.ptype = random.choices(
                ["life", "score", "speed", "fastfire", "splitfire"],
                weights=[10, 50, 20, 30, 10],
                k=1,
            )[0]

    def update(self, dt, game):
        self.y += self.y_speed * dt

        if self.y < -50:
            self.deactivate()

    def apply(self, game: "GameWindow"):
        self.deactivate()
        match self.ptype:
            case "life":
                game.lives += 1
            case "score":
                game.score += 500
            case "speed":
                game.player.accel = min(30, game.player.accel + 5)
            case "fastfire":
                game.fire_rate = 0.05

                last_entry = game.Scheduler.cancel_schedule(self.stopfastfire)
                time = (last_entry[2] if last_entry else 0) + 10 * 60
                game.Scheduler.schedule_update(self.stopfastfire, time, (game,))
            case "splitfire":
                game.split_fire = True

                last_entry = game.Scheduler.cancel_schedule(self.stopsplitfire)
                time = (last_entry[2] if last_entry else 0) + 10 * 60
                game.Scheduler.schedule_update(self.stopsplitfire, time, (game,))

    @staticmethod
    def stopfastfire(game):
        game.fire_rate = 0.15

    @staticmethod
    def stopsplitfire(game):
        game.split_fire = False
