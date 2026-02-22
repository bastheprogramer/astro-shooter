import pyglet
import math
from pyglet.window import key

class Player(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = 0.1
        self.velocity_x = 0
        self.velocity_y = 0
        self.drag = 0.95  # Physics drag
        self.accel = 20.0 # Acceleration speed
        self.is_vulnerable = True

    def apply_drag(self):
        self.velocity_x *= self.drag
        self.velocity_y *= self.drag
    
    def update(self, dt, keys, mouse_x, mouse_y):
        # 1. Rotation (Smooth LERP to mouse)
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        
        # Calculate target angle (Pyglet uses clockwise degrees)
        # Note: Added +90 assuming your sprite's original image faces straight UP. 
        # If it faces RIGHT, you might not need the +90.
        target_angle = -math.degrees(math.atan2(dy, dx)) + 90
        
        # Calculate the shortest distance between current and target angle (-180 to 180)
        angle_diff = (target_angle - self.rotation + 180) % 360 - 180
        
        # LERP Factor: Higher number = snappier, Lower number = "floatier"
        turn_speed = 15.0 
        
        # Ease the rotation towards the target
        self.rotation += angle_diff * (turn_speed * dt)
        self.rotation %= 360

        # 2. Movement (WASD)
        if keys[key.W]: self.velocity_y += self.accel
        if keys[key.S]: self.velocity_y -= self.accel
        if keys[key.A]: self.velocity_x -= self.accel
        if keys[key.D]: self.velocity_x += self.accel
        
        self.apply_drag()
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt