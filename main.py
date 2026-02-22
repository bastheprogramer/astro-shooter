import pyglet
import os
import random
from typing import List, Union

from entities.player import Player
from entities.laser import Laser
from entities.asteroid import Asteroid
from entities.explosion import Explosion
from entities.powerup import PowerUp
from entities.tracking_missile import TrackingMissile
from highscore import LoadHighScore, SaveHighScore
from resources import ResourceManager
from gamestate import GameState
from utils import are_sprites_colliding
from Weapons import WeaponType
from Scheduler import Scheduler
# Constants
WIDTH, HEIGHT = 800, 600
FIXED_DT = 1 / 60.0

base_dir = os.path.dirname(__file__)

# Load Assets via ResourceManager (will raise helpful errors if missing)
_rm = ResourceManager(base_dir)
registry = _rm.load_resources()

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
        cursor = pyglet.window.ImageMouseCursor(registry.sprite("cursor"), 0, 0)
        self.set_mouse_cursor(cursor)

        # Game Objects
        self.player = Player(registry.sprite("player"), WIDTH//2, HEIGHT//2, self.batch)
        self.weapons: List[Union[Laser, TrackingMissile]] = []
        self.asteroids: List[Asteroid] = []
        self.explosions: List[Explosion] = []
        self.powerups: List[PowerUp] = []

        # State
        self.score = 0
        self.lives = 3
        self.high_score = LoadHighScore()
        self.game_state = GameState.Menu
        
        # Scheduler
        self.Scheduler = Scheduler()
        
        # Shooting
        self.is_firing = False
        self.fire_cooldown = 0
        self.fire_rate = 0.15  # Base fire rate
        self.unlocked_weapon = [WeaponType.Laser]
        self.weapon = WeaponType.Laser
        
        # Spawning
        self.asteroid_spawn_rate = 2  # % chance per frame
        
        # Audio
        self.bg_player = registry.sound("music").play()
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
        self.score = 30000
        self.lives = 3
        self.weapons.clear()
        self.asteroids.clear()
        self.explosions.clear()
        self.powerups.clear()
        self.player.x, self.player.y = WIDTH // 2, HEIGHT // 2
        self.player.velocity_x, self.player.velocity_y = 0, 0
        self.fire_rate = 0.15
        self.asteroid_spawn_rate = 2
        self.weapon = WeaponType.Laser
        self.unlocked_weapon = [WeaponType.Laser]

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and self.game_state == GameState.Playing:
            self.is_firing = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.is_firing = False

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            if self.game_state != GameState.Playing:
                self.game_state = GameState.Playing
                self.lbl_center.visible = False
                self.reset_game()
        if symbol in (pyglet.window.key._1, pyglet.window.key._2):
            if self.game_state == GameState.Playing:
                index = symbol - pyglet.window.key._1
                if index < len(self.unlocked_weapon):
                    self.weapon = self.unlocked_weapon[index]
        if symbol == pyglet.window.key.ESCAPE and self.game_state == GameState.Playing:
            self.game_state = GameState.Paused
            self.lbl_center.text = "PAUSED\n\nPRESS ESC TO RESUME"
            self.lbl_center.visible = True
        elif symbol == pyglet.window.key.ESCAPE and self.game_state == GameState.Paused:
            self.game_state = GameState.Playing
            self.lbl_center.visible = False
            

        
    
    def update(self, dt):
        if self.game_state != GameState.Playing:
            return
        
        # Update scheduler tasks
        self.Scheduler.update_schedule()

        # Update Player (with bounds)
        self.player.update(dt, self.keys, self.mouse_x, self.mouse_y)
        self.player.x = max(20, min(WIDTH-20, self.player.x))
        self.player.y = max(20, min(HEIGHT-20, self.player.y))

        
        # Shooting
        self.fire_cooldown -= dt
        if self.is_firing and self.fire_cooldown <= 0:
            self.fire_cooldown = self.fire_rate
            
            match self.weapon:
                case WeaponType.Laser:
                    registry.sound("laser").play()
                    self.weapons.append(Laser(registry.sprite("laser"), self.player.x, self.player.y, 
                                    self.player.rotation, self.batch))
                case WeaponType.TrackingMissile:
                    registry.sound("missile").play()
                    self.weapons.append(TrackingMissile(registry.sprite("missile"), self.player.x, self.player.y,
                                    self.player.rotation, self.batch, self.asteroids))
        

        # Update Lasers
        for weapon in self.weapons[:]:
            weapon.update(dt, WIDTH, HEIGHT)
            if not weapon.active:
                weapon.delete()
                self.weapons.remove(weapon)

        # Spawn Asteroids
        if random.randint(0, 100) < self.asteroid_spawn_rate:
            self.spawn_asteroid()

        # Update Asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update(dt, WIDTH, HEIGHT)
            
            # weapon collision
            hit = False
            for weapon in self.weapons[:]:
                if not (weapon.active and asteroid.active and are_sprites_colliding(weapon, asteroid)):
                    continue
                
                weapon.active = False
                weapon.delete()
                self.weapons.remove(weapon)
                
                # Create explosion
                self.explosions.append(Explosion(asteroid.x, asteroid.y, self.batch, registry.sprite("explosion")))
                registry.sound("explosion").play()
                
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
            if are_sprites_colliding(asteroid, self.player):
                registry.sound("explosion").play()
                self.explosions.append(Explosion(asteroid.x, asteroid.y, self.batch, registry.sprite("explosion")))
                if self.player.is_vulnerable:
                    self.lives -= 1
                    self.player.is_vulnerable = False
                    self.Scheduler.schedule_update(lambda player: setattr(player, 'is_vulnerable', True), 5, (self.player,)) # 5 ticks of invulnerability
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
            
            if are_sprites_colliding(powerup, self.player):
                ptype = powerup.apply()
                registry.sound("powerup").play()
                powerup.delete()
                self.powerups.remove(powerup)
                
                # Apply powerup effects
                match ptype:
                    case "life":
                        self.lives += 1
                    case "score":
                        self.score += 500
                    case "speed":
                        self.player.accel = min(30, self.player.accel + 5)
                    case "fastfire":
                        self.fire_rate = 0.05  # Much faster shooting
                        
                        last_entry = self.Scheduler.cancel_schedule(lambda: setattr(self, 'fire_rate', 0.15))  # Cancel any existing reset tasks
                        time = last_entry[2] if last_entry else 0 + 10*60
                        self.Scheduler.schedule_update(lambda: setattr(self, 'fire_rate', 0.15), time)  # Reset after 10 seconds               
            elif not powerup.active:
                powerup.delete()
                self.powerups.remove(powerup)

        # Update UI
        self.lbl_score.text = f"Score: {self.score}"
        self.lbl_lives.text = f"Lives: {self.lives}"
        
        if self.score > self.high_score:
            self.high_score = self.score
            SaveHighScore(self.score)
            self.lbl_high.text = f"High Score: {self.high_score}"
            
        
        # Increase difficulty
        if self.score > 5000 and self.asteroid_spawn_rate < 5:
            self.asteroid_spawn_rate = 3
        if self.score > 15000 and self.asteroid_spawn_rate < 7:
            self.asteroid_spawn_rate = 5
        
        if self.score > 15000 and WeaponType.TrackingMissile not in self.unlocked_weapon:
            self.unlocked_weapon.append(WeaponType.TrackingMissile)
            self.lbl_center.text = "Tracking Missile unlocked\n press 2 to use"
            self.lbl_center.visible = True
            self.Scheduler.schedule_frame(lambda text: setattr(text, "visible", False), 120, (self.lbl_center,))  # Hide after 2 seconds

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
            
        self.asteroids.append(Asteroid(registry.sprite("asteroid"), self.batch, x, y, vx, vy))

    def spawn_powerup(self, x, y):
        self.powerups.append(PowerUp(registry.sprite("powerup"), x, y, self.batch))

    def game_over(self):
        self.game_state = GameState.GameOver
        if self.score > self.high_score:
            self.high_score = self.score
            SaveHighScore(self.score)
            self.lbl_high.text = f"High Score: {self.high_score}"
            self.lbl_center.text = "NEW HIGH SCORE!\n\nGAME OVER\nPRESS ENTER TO RESTART"
        else:
            self.lbl_center.text = "GAME OVER\n\nPRESS ENTER TO RESTART"
        self.lbl_center.visible = True

    def on_draw(self):
        self.clear()
        self.Scheduler.update_frame()
        self.batch.draw()

if __name__ == "__main__":
    game = GameWindow()
    pyglet.app.run()
