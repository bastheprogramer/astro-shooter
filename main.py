import pyglet
import os
import random
from typing import List

from player import Player
from laser import Laser
from asteroid import Asteroid
from explosion import Explosion
from powerup import PowerUp
from highscore import load_high_score, save_high_score

# Constants
WIDTH, HEIGHT = 800, 600
FIXED_DT = 1 / 60.0

def center_anchor(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img

base_dir = os.path.dirname(__file__)
sprite_dir = os.path.join(base_dir, 'sprites')
sound_dir = os.path.join(base_dir, 'sounds')

# Load Assets
res = {
    "player": center_anchor(pyglet.image.load(os.path.join(sprite_dir, "player.png"))),
    "laser": center_anchor(pyglet.image.load(os.path.join(sprite_dir, "lazer.png"))),
    "asteroid": center_anchor(pyglet.image.load(os.path.join(sprite_dir, "astrode.png"))),
    "explosion": center_anchor(pyglet.image.load(os.path.join(sprite_dir, "explosion.png"))),
    "powerup": center_anchor(pyglet.image.load(os.path.join(sprite_dir, "powerup.png"))),
    "cursor": pyglet.image.load(os.path.join(sprite_dir, "pointer.png"))
}

# Sounds
sfx = {
    "laser": pyglet.media.load(os.path.join(sound_dir, "laserShoot.wav"), streaming=False),
    "explosion": pyglet.media.load(os.path.join(sound_dir, "explosion.wav"), streaming=False),
    "powerup": pyglet.media.load(os.path.join(sound_dir, "powerUp.wav"), streaming=False),
    "music": pyglet.media.load(os.path.join(sound_dir, "background.wav"), streaming=True)
}

class GameWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(width=WIDTH, height=HEIGHT, caption="Astro Shooter", resizable=False)
        self.batch = pyglet.graphics.Batch()
        
        # Input
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.mouse_x = WIDTH // 2
        self.mouse_y = HEIGHT // 2
        
        # Cursor
        cursor = pyglet.window.ImageMouseCursor(res["cursor"], 0, 0)
        self.set_mouse_cursor(cursor)

        # Game Objects
        self.player = Player(res["player"], WIDTH//2, HEIGHT//2, self.batch)
        self.lasers: List[Laser] = []
        self.asteroids: List[Asteroid] = []
        self.explosions: List[Explosion] = []
        self.powerups: List[PowerUp] = []

        # State
        self.score = 0
        self.lives = 3
        self.high_score = load_high_score()
        self.game_state = "menu"
        
        # Shooting
        self.is_firing = False
        self.fire_cooldown = 0
        self.fire_rate = 0.15  # Base fire rate
        self.fire_rate_timer = 0  # Timer for temporary powerup
        
        # Spawning
        self.powerup_timer = 0
        self.asteroid_spawn_rate = 2  # % chance per frame
        
        # Audio
        self.bg_player = sfx["music"].play()
        self.bg_player.loop = True
        self.bg_player.volume = 0.3
        
        # UI
        self.lbl_score = pyglet.text.Label("Score: 0", x=10, y=HEIGHT-30, batch=self.batch, font_size=14, bold=True)
        self.lbl_lives = pyglet.text.Label("Lives: 3", x=10, y=HEIGHT-55, batch=self.batch, font_size=14, bold=True)
        self.lbl_high = pyglet.text.Label(f"High Score: {self.high_score}", x=10, y=HEIGHT-80, batch=self.batch, font_size=12)
        self.lbl_center = pyglet.text.Label("ASTRO SHOOTER\n\nPRESS ENTER TO START", 
                                            x=WIDTH//2, y=HEIGHT//2, 
                                            anchor_x='center', anchor_y='center', 
                                            batch=self.batch, font_size=20, bold=True,
                                            multiline=True, width=400, align='center')

        pyglet.clock.schedule_interval(self.update, FIXED_DT)

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.lasers.clear()
        self.asteroids.clear()
        self.explosions.clear()
        self.powerups.clear()
        self.player.x, self.player.y = WIDTH // 2, HEIGHT // 2
        self.player.velocity_x, self.player.velocity_y = 0, 0
        self.powerup_timer = 0
        self.fire_rate = 0.15
        self.fire_rate_timer = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and self.game_state == "playing":
            self.is_firing = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.is_firing = False

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            if self.game_state != "playing":
                self.game_state = "playing"
                self.lbl_center.visible = False
                self.reset_game()

    def update(self, dt):
        if self.game_state != "playing":
            return

        # Update Player (with bounds)
        self.player.update(dt, self.keys, self.mouse_x, self.mouse_y)
        self.player.x = max(20, min(WIDTH-20, self.player.x))
        self.player.y = max(20, min(HEIGHT-20, self.player.y))

        # Shooting
        self.fire_cooldown -= dt
        if self.is_firing and self.fire_cooldown <= 0:
            self.fire_cooldown = self.fire_rate
            sfx["laser"].play()
            self.lasers.append(Laser(res["laser"], self.player.x, self.player.y, 
                                    self.player.rotation, self.batch))
        
        # Fast fire powerup timer
        if self.fire_rate_timer > 0:
            self.fire_rate_timer -= dt
            if self.fire_rate_timer <= 0:
                self.fire_rate = 0.15  # Reset to normal

        # Update Lasers
        for laser in self.lasers[:]:
            laser.update(dt, WIDTH, HEIGHT)
            if not laser.active:
                laser.delete()
                self.lasers.remove(laser)

        # Spawn Asteroids
        if random.randint(0, 100) < self.asteroid_spawn_rate:
            self.spawn_asteroid()

        # Update Asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update(dt, WIDTH, HEIGHT)
            
            # Laser collision
            hit = False
            for laser in self.lasers[:]:
                if laser.active and asteroid.active and laser.collides_with(asteroid):
                    laser.active = False
                    laser.delete()
                    self.lasers.remove(laser)
                    
                    # Create explosion
                    self.explosions.append(Explosion(asteroid.x, asteroid.y, self.batch, res["explosion"]))
                    sfx["explosion"].play()
                    
                    # Score based on size
                    self.score += int(100 * asteroid.scale)
                    
                    # Spawn fragments
                    fragments = asteroid.explode()
                    self.asteroids.extend(fragments)
                    asteroid.delete()
                    
                    # Chance to drop powerup
                    if random.random() < 0.15:
                        self.spawn_powerup(asteroid.x, asteroid.y)
                    
                    hit = True
                    break
            
            if hit:
                self.asteroids.remove(asteroid)
                continue
                
            if not asteroid.active:
                asteroid.delete()
                self.asteroids.remove(asteroid)
                continue

            # Player collision
            dx = asteroid.x - self.player.x
            dy = asteroid.y - self.player.y
            if (dx*dx + dy*dy) < 1600:
                sfx["explosion"].play()
                self.explosions.append(Explosion(asteroid.x, asteroid.y, self.batch, res["explosion"]))
                self.lives -= 1
                asteroid.active = False
                asteroid.delete()
                self.asteroids.remove(asteroid)
                
                if self.lives <= 0:
                    self.game_over()

        # Update Explosions
        for explosion in self.explosions[:]:
            if not explosion.update(dt):
                explosion.sprite.delete()
                self.explosions.remove(explosion)

        # Update PowerUps
        for powerup in self.powerups[:]:
            powerup.update(dt)
            
            if powerup.collides_with(self.player):
                ptype = powerup.apply()
                sfx["powerup"].play()
                powerup.delete()
                self.powerups.remove(powerup)
                
                # Apply powerup effects
                if ptype == "life":
                    self.lives += 1
                elif ptype == "score":
                    self.score += 500
                elif ptype == "speed":
                    self.player.accel = min(30, self.player.accel + 5)
                elif ptype == "fastfire":
                    self.fire_rate = 0.05  # Much faster shooting
                    self.fire_rate_timer = 10  # Lasts 10 seconds
                    
            elif not powerup.active:
                powerup.delete()
                self.powerups.remove(powerup)

        # Update UI
        self.lbl_score.text = f"Score: {self.score}"
        self.lbl_lives.text = f"Lives: {self.lives}"
        
        # Increase difficulty
        if self.score > 5000 and self.asteroid_spawn_rate < 5:
            self.asteroid_spawn_rate = 3
        if self.score > 15000 and self.asteroid_spawn_rate < 7:
            self.asteroid_spawn_rate = 5

    def spawn_asteroid(self):
        side = random.choice(['top', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = HEIGHT + 50
            vx = random.uniform(-100, 100)
            vy = random.uniform(-200, -100)
        elif side == 'left':
            x = -50
            y = random.randint(0, HEIGHT)
            vx = random.uniform(100, 200)
            vy = random.uniform(-50, 50)
        else:  # right
            x = WIDTH + 50
            y = random.randint(0, HEIGHT)
            vx = random.uniform(-200, -100)
            vy = random.uniform(-50, 50)
            
        self.asteroids.append(Asteroid(res["asteroid"], self.batch, x, y, vx, vy))

    def spawn_powerup(self, x, y):
        self.powerups.append(PowerUp(res["powerup"], x, y, self.batch))

    def game_over(self):
        self.game_state = "gameover"
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.score)
            self.lbl_high.text = f"High Score: {self.high_score}"
            self.lbl_center.text = "NEW HIGH SCORE!\n\nGAME OVER\nPRESS ENTER TO RESTART"
        else:
            self.lbl_center.text = "GAME OVER\n\nPRESS ENTER TO RESTART"
        self.lbl_center.visible = True

    def on_draw(self):
        self.clear()
        self.batch.draw()

if __name__ == "__main__":
    game = GameWindow()
    pyglet.app.run()