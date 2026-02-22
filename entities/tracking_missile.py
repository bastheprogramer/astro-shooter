import pyglet
import math
import random
from entities.asteroid import Asteroid

class TrackingMissile(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, rotation, batch, astroids):
        super().__init__(img, x=x, y=y, batch=batch)
        self.rotation = rotation
        self.speed = 400
        self.active = True
        self.astroids = astroids
        
        # FOV settings
        self.fov = 40 
        
        # Pick an initial target from the FOV
        self.target = self.find_target_in_fov()
        
        # If no target in FOV at launch, you could either not fire 
        # or just fly straight (current behavior)
    
    def find_target_in_fov(self):
        """Scans asteroids and returns a random one within the 20-degree FOV."""
        possible_targets = []
        
        for asteroid in self.asteroids:
            if not asteroid.active:
                continue
                
            # 1. Get angle to this specific asteroid
            dx = asteroid.x - self.x
            dy = asteroid.y - self.y
            angle_to_asteroid = math.degrees(math.atan2(dx, dy))
            
            # 2. Calculate angular difference (Shortest path)
            # This tells us how many degrees we'd have to turn to face it
            diff = (angle_to_asteroid - self.rotation + 180) % 360 - 180
            
            # 3. Check if it's within our FOV (half of 20 on each side)
            if abs(diff) <= self.fov / 2:
                possible_targets.append(asteroid)
        
        if possible_targets:
            return random.choice(possible_targets)
        return None

    def track_target(self, dt):
        # If no target, or target died, try to find a new one in FOV
        if not self.target or not self.target.active:
            self.target = self.find_target_in_fov()
            if not self.target:
                return # Keep flying straight if nothing is in view

        # Calculate target angle
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        target_angle = math.degrees(math.atan2(dx, dy))

        # Shortest path steering
        angle_diff = (target_angle - self.rotation + 180) % 360 - 180
        
        # Steer towards the target
        turn_speed = 7.0  # Increased slightly for more aggressive tracking
        self.rotation += angle_diff * (turn_speed * dt)
        self.rotation %= 360
    
    def update(self, dt, width, height):
        self.track_target(dt)
        
        # Movement math
        rads = math.radians(self.rotation)
        self.x += math.sin(rads) * self.speed * dt
        self.y += math.cos(rads) * self.speed * dt

        # Bounds check
        if self.x < -50 or self.x > width + 50 or self.y < -50 or self.y > height + 50:
            self.active = False