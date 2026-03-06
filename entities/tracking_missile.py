import math
import random
from typing import TYPE_CHECKING

from entities.asteroid import asteroid
from entities.gameobject import gameobject

if TYPE_CHECKING:
    from main import GameWindow


class tracking_missile(gameobject):
    def __init__(self, img, x, y, rotation, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = 400

        # FOV settings
        self.fov = 40
        self.target: asteroid = None

    def find_target_in_fov(self, game: "GameWindow"):
        """Scans asteroids and returns a random one within the 20-degree FOV."""
        possible_targets = []

        for candidate in game.asteroids:
            if not candidate.active:
                continue

            dx = candidate.x - self.x
            dy = candidate.y - self.y
            angle_to_asteroid = math.degrees(math.atan2(dx, dy))

            diff = (angle_to_asteroid - self.rotation + 180) % 360 - 180

            if abs(diff) <= self.fov / 2:
                possible_targets.append(candidate)

        if possible_targets:
            return random.choice(possible_targets)
        return None

    def track_target(self, dt, game: "GameWindow"):
        if not self.target or not self.target.active:
            self.target = self.find_target_in_fov(game)
            if not self.target:
                return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        target_angle = math.degrees(math.atan2(dx, dy))

        angle_diff = (target_angle - self.rotation + 180) % 360 - 180

        turn_speed = 7.0
        self.rotation += angle_diff * (turn_speed * dt)
        self.rotation %= 360

    def update(self, dt, game: "GameWindow"):
        self.track_target(dt, game)

        rads = math.radians(self.rotation)
        self.x += math.sin(rads) * self.speed * dt
        self.y += math.cos(rads) * self.speed * dt

        if self.is_out_of_bounds(game.width, game.height, margin=50):
            self.deactivate()
