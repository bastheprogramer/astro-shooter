import pyglet
import os
import random
import numpy as np
import time
import psutil
from typing import List, Union

from entities.player import player
from entities.laser import laser
from entities.asteroid import asteroid
from entities.explosion import explosion
from entities.powerup import powerup
from entities.tracking_missile import tracking_missile
from highscore import load_high_score, save_high_score
from resources import resource_manager
from gamestate import game_state
from utils import are_sprites_colliding
from Weapons import WeaponType
from Scheduler import scheduler

import tracemalloc

tracemalloc.start()

# Constants
WIDTH, HEIGHT = 800, 600
FIXED_DT = 1 / 60.0

base_dir = os.path.dirname(__file__)

# Load Assets via ResourceManager (will raise helpful errors if missing)
_rm = resource_manager(base_dir)
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
        self.player = player(registry.sprite("player"), WIDTH//2, HEIGHT//2, self.batch)
        self.weapons: List[Union[laser, tracking_missile]] = []
        self.asteroids: List[asteroid] = []
        self.explosions: List[explosion] = []
        self.powerups: List[powerup] = []

        # State
        self.score = 0
        self.lives = 3
        self.high_score = load_high_score()
        self.game_state = game_state.Menu
        
        # Scheduler
        self.Scheduler: scheduler = scheduler()
        
        
        # Shooting
        self.is_firing = False
        self.fire_cooldown = 0
        self.fire_rate = 0.15  # Base fire rate
        self.unlocked_weapon = [WeaponType.Laser]
        self.weapon = WeaponType.Laser
        self.split_fire = False
        
        # Spawning
        self.asteroid_spawn_rate = 2  # % chance per frame
        
        # Audio
        self.bg_player = registry.sound("music")
        self.bg_player.play()
        self.bg_player.loop = True
        self.bg_player.volume = 0.3
        
        # Debug
        self.debug = False
        self.tps = 1/FIXED_DT
        self.last_time_fps = time.perf_counter()
        self.msize: int = 0
        self.fps = 0
        self.auto = False
        # UI
        self.lbl_score = pyglet.text.Label("Score: 0", x=10, y=HEIGHT-30, batch=self.batch, font_size=14, bold=True)
        self.lbl_lives = pyglet.text.Label("Lives: 3", x=10, y=HEIGHT-55, batch=self.batch, font_size=14, bold=True)
        self.lbl_high = pyglet.text.Label(f"High Score: {self.high_score}", x=10, y=HEIGHT-80, batch=self.batch, font_size=12)
        self.lbl_debug = pyglet.text.Label("", x=WIDTH-10, y=HEIGHT-30, batch=self.batch, font_size=12, anchor_x='right', multiline=True, width=200)
        self.lbl_debug.visible = self.debug
        self.lbl_center = pyglet.text.Label("ASTRO SHOOTER\n\nPRESS ENTER TO START", 
                                            x=WIDTH//2, y=HEIGHT//2, 
                                            anchor_x='center', anchor_y='center', 
                                            batch=self.batch, font_size=20, bold=True,
                                            multiline=True, width=400, align='center')
        
        
        pyglet.clock.schedule_interval(self.update, FIXED_DT)
        pyglet.clock.schedule_interval(self.update_debug, 1/2)  # Update debug info every second
        
    def update_debug(self, dt):
        # Place to update any debug info that doesn't need to be updated every frame
        self.msize = psutil.Process(os.getpid()).memory_info().rss
        self.lbl_debug.text = f"""
        FPS: {self.fps:.2f}
        TPS: {self.tps:.2f}
        Asteroids: {len(self.asteroids)}
        Weapons: {len(self.weapons)}
        PowerUps: {len(self.powerups)}
        Spawn Rate: {self.asteroid_spawn_rate:.2f}
        Memory Usage: {self.msize/(2**20):.2f} MiB
        """
    
    def on_close(self):
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        print("[ Top 10 memory allocations ]")
        for stat in top_stats[:10]:
            print(stat)
        return super().on_close()
    def reset_game(self):
        self.score = 0
        self.lives = 3
        def clear_entitys(l: List):
            for item in l:
                item.delete()
            l.clear()
        clear_entitys(self.weapons)
        clear_entitys(self.asteroids)
        clear_entitys(self.explosions)
        clear_entitys(self.powerups)
        
        self.player.is_vulnerable = True

        self.Scheduler.cancel_all()
        
        self.player.x, self.player.y = WIDTH // 2, HEIGHT // 2
        self.player.velocity_x, self.player.velocity_y = 0, 0
        
        self.split_fire = False
        self.fire_rate = 0.15
        self.asteroid_spawn_rate = 2
        self.weapon = WeaponType.Laser
        self.unlocked_weapon = [WeaponType.Laser, WeaponType.TrackingMissile]

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and self.game_state == game_state.Playing:
            self.is_firing = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.is_firing = False

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            if self.game_state != game_state.Playing and self.game_state != game_state.Paused:
                self.game_state = game_state.Playing
                self.lbl_center.visible = False
                self.reset_game()

        if symbol in (pyglet.window.key._1, pyglet.window.key._2):
            if self.game_state == game_state.Playing:
                index = symbol - pyglet.window.key._1
                if index < len(self.unlocked_weapon):
                    self.weapon = self.unlocked_weapon[index]
        
        if symbol == pyglet.window.key.ESCAPE and self.game_state == game_state.Playing:
            self.game_state = game_state.Paused
            self.lbl_center.text = "PAUSED\n\nPRESS ESC TO RESUME"
            self.lbl_center.visible = True
        elif symbol == pyglet.window.key.ESCAPE and self.game_state == game_state.Paused:
            self.game_state = game_state.Playing
            self.lbl_center.visible = False
        
        # debug
        if symbol == pyglet.window.key.P:
            self.debug = not self.debug
            if not self.debug:
                self.auto = False
            self.lbl_debug.visible = self.debug
            print(f"Debug mode {'enabled' if self.debug else 'disabled'}")
        
        if symbol == pyglet.window.key.O and self.debug:
            self.auto = not self.auto
            print(f"Auto mode {'enabled' if self.auto else 'disabled'}")

    def update(self, dt):
        if self.game_state != game_state.Playing:
            return
        
        # Update scheduler tasks
        self.Scheduler.update_schedule(dt)

        # Update Player (with bounds)
        self.player.update(dt, self.keys, self.mouse_x, self.mouse_y)
        self.player.x = max(20, min(WIDTH-20, self.player.x))
        self.player.y = max(20, min(HEIGHT-20, self.player.y))
        
        # debug for memory leaks/ aim bot
        closest_asteroid: asteroid = min(self.asteroids, key=lambda a: (a.x - self.player.x)**2 + (a.y - self.player.y)**2, default=None)
        closest_powerup: powerup = min(self.powerups, key=lambda p: (p.x - self.player.x)**2 + (p.y - self.player.y)**2, default=None)
        if self.auto:
            # Always aim and fire at closest asteroid
            if closest_asteroid and self.debug:
                self.is_firing = True
                distance = ((closest_asteroid.x - self.player.x)**2 + (closest_asteroid.y - self.player.y)**2)**0.5
                self.mouse_x = closest_asteroid.x + closest_asteroid.vel_x * dt * distance * 0.1
                self.mouse_y = closest_asteroid.y + closest_asteroid.vel_y * dt * distance * 0.1

            DANGER_RADIUS = 120  # pixels — how close an asteroid must be before dodging

            # Sum a repulsion vector from all nearby asteroids
            avoid_x, avoid_y = 0.0, 0.0
            for ast in self.asteroids:
                dx = self.player.x - ast.x
                dy = self.player.y - ast.y
                dist = (dx**2 + dy**2) ** 0.5
                if 0 < dist < DANGER_RADIUS:
                    weight = (DANGER_RADIUS - dist) / DANGER_RADIUS  # closer = stronger push
                    avoid_x += (dx / dist) * weight
                    avoid_y += (dy / dist) * weight

            avoiding = (avoid_x**2 + avoid_y**2) ** 0.5 > 0.1

            if avoiding and self.debug:
                # Dodge away from nearby asteroids
                move_x = avoid_x
                move_y = avoid_y
            elif closest_powerup and self.debug:
                # No danger — chase the nearest powerup
                move_x = closest_powerup.x - self.player.x
                move_y = closest_powerup.y - self.player.y
            else:
                move_x = self.width/2 - self.player.x
                move_y = self.height/2 - self.player.y

            # Convert desired direction into key presses
            if self.debug:
                self.keys.data[pyglet.window.key.A] = move_x < -0.1
                self.keys.data[pyglet.window.key.D] = move_x > 0.1
                self.keys.data[pyglet.window.key.S] = move_y < -0.1
                self.keys.data[pyglet.window.key.W] = move_y > 0.1

        # Shooting
        self.fire_cooldown -= dt
        if self.is_firing and self.fire_cooldown <= 0:
            self.fire_cooldown = self.fire_rate

            weapon_str = self.weapon.value
            Weapon_to_spawn = WeaponType.str_to_class(weapon_str)
            
            registry.play(weapon_str)
            if self.split_fire:
                self.weapons.append(Weapon_to_spawn(registry.sprite(weapon_str), self.player.x, self.player.y, self.player.rotation - 10, self.batch))
                self.weapons.append(Weapon_to_spawn(registry.sprite(weapon_str), self.player.x, self.player.y, self.player.rotation + 10, self.batch))
            self.weapons.append(Weapon_to_spawn(registry.sprite(weapon_str), self.player.x, self.player.y, self.player.rotation, self.batch))

        # Update Lasers/ Missiles
        for weapon in self.weapons[:]:
            weapon.update(dt, self)
            if not weapon.active:
                weapon.delete()
                self.weapons.remove(weapon)

        # Spawn Asteroids
        if random.randrange(0, 100) < self.asteroid_spawn_rate:
            self.spawn_asteroid()

        # Update Asteroids
        for ast in self.asteroids[:].copy():
            ast.update(dt, self)
            
            # weapon collision
            hit = False
            for weapon in self.weapons[:]:
                if not (weapon.active and ast.active and are_sprites_colliding(weapon, ast)):
                    continue
                
                weapon.active = False
                weapon.delete()
                self.weapons.remove(weapon)
                
                # Chance to drop powerup
                if random.random() < 0.15:
                    self.spawn_powerup(ast.x, ast.y)
                
                hit = True
                break
            
            if hit:
                # Spawn fragments
                fragments = ast.explode()
                self.asteroids.extend(fragments)
                ast.delete()
                self.asteroids.remove(ast)
                
                # Create explosion
                self.explosions.append(explosion(registry.sprite("explosion"), ast.x, ast.y, self.batch, self.Scheduler))
                registry.play("explosion")
                
                # Score based on size
                self.score += int(100 * ast.scale)
                continue
            
            if not ast.active:
                ast.delete()
                self.asteroids.remove(ast)
                continue
            
            # Player collision
            if are_sprites_colliding(ast, self.player):
                registry.play("explosion")
                self.explosions.append(explosion(registry.sprite("explosion"), self.player.x, self.player.y, self.batch, self.Scheduler))
                if self.player.is_vulnerable:
                    self.lives -= 1
                    self.player.is_vulnerable = False
                    self.Scheduler.schedule_update(lambda player: setattr(player, 'is_vulnerable', True), 5, (self.player,)) # 5 ticks of invulnerability
                ast.active = False
                ast.delete()
                self.asteroids.remove(ast)
                
                if self.lives <= 0:
                    self.game_over()

        # Update Explosions
        for exp in self.explosions[:]:
            if exp.active:
                continue
            exp.delete()
            self.explosions.remove(exp)

        # Update PowerUps
        for powup in self.powerups[:]:
            powup.update(dt)
            
            if are_sprites_colliding(powup, self.player):
                powup.apply(self)
                registry.play("powerup")
                powup.delete()
                self.powerups.remove(powup)

            elif not powup.active:
                powup.delete()
                self.powerups.remove(powup)

        # Update UI
        self.lbl_score.text = f"Score: {self.score}"
        self.lbl_lives.text = f"Lives: {self.lives}"
        
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.score)
            self.lbl_high.text = f"High Score: {self.high_score}"
            
        
        # Increase difficulty
        self.asteroid_spawn_rate = (6.69578)/(1+np.exp(-((0.000128988*self.score)-0.853516)))
        """
        log formula for spawn rate:
        f(0) = 2
        f(5000) = 3
        f(15000) = 5
        """
        
        
        if WeaponType.tracking_missile_condition(score=self.score) and WeaponType.TrackingMissile not in self.unlocked_weapon:
            self.unlocked_weapon.append(WeaponType.TrackingMissile)
            self.lbl_center.text = "Tracking Missile unlocked\n press 2 to use"
            self.lbl_center.visible = True
            self.Scheduler.schedule_frame(lambda text: setattr(text, "visible", False), 120, (self.lbl_center,))  # Hide after 2 seconds
        
        self.tps = 1/dt

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
        size_1_percent = (122.42384) / (1 + np.exp(-((-0.340352 * self.asteroid_spawn_rate) + 0.310192)))
        size_2_percent = 35
        size_3_percent = (3500650.29) / (1 + np.exp(-((0.256397 * self.asteroid_spawn_rate) - 12.8732)))
        

        type_val = random.choices([1, 2, 3], weights=[size_1_percent, size_2_percent, size_3_percent])[0]
        size = [0.126, 0.21, 0.35][type_val-1]
        self.asteroids.append(asteroid(registry.sprite("asteroid"), self.batch, x, y, vx, vy, type_val=type_val, size= size))

    def spawn_powerup(self, x, y):
        self.powerups.append(powerup(registry.sprite("powerup"), x, y, self.batch))

    def game_over(self):
        self.game_state = game_state.GameOver
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
        current_time = time.perf_counter()
        dt = current_time - self.last_time_fps
        self.last_time_fps = current_time
        self.Scheduler.update_frame(dt)
        self.lbl_debug.visible = self.debug
        self.fps = dt**-1
        self.batch.draw()

if __name__ == "__main__":
    game = GameWindow()
    pyglet.app.run()
