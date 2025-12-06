import pyglet
import random
import math

class Asteroid(pyglet.sprite.Sprite):
    def __init__(self, img, batch, x, y, speed_x, speed_y, size=0.35, type_val=3):
        super().__init__(img, x=x, y=y, batch=batch)
        self.scale = size
        self.type_val = type_val
        self.rotation_speed = random.uniform(-50, 50)
        self.vel_x = speed_x
        self.vel_y = speed_y
        self.active = True

    def update(self, dt, width, height):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.rotation += self.rotation_speed * dt

        # Simple bounds check
        if (self.x < -50 or self.x > width + 50 or 
            self.y < -50 or self.y > height + 50):
            self.active = False

    def explode(self):
        self.active = False
        if self.type_val <= 1:
            return []

        fragments = []
        num_frags = random.randint(2, 4)
        for _ in range(num_frags):
            # Create variation in speed and angle
            angle_var = math.radians(random.uniform(0, 360))
            speed_base = math.sqrt(self.vel_x**2 + self.vel_y**2) * 1.5
            
            new_vx = math.sin(angle_var) * speed_base
            new_vy = math.cos(angle_var) * speed_base
            
            frag = Asteroid(
                img=self.image,
                batch=self.batch,
                x=self.x,
                y=self.y,
                speed_x=new_vx,
                speed_y=new_vy,
                size=self.scale * 0.6,
                type_val=self.type_val - 1
            )
            fragments.append(frag)
        return fragments