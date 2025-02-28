import pyglet
import random
import gc
import astrod
import lazer
import player
import os
from highscore import load_high_score, save_high_score
from explosion import Explosion
from powerup import PowerUp
from quadtree import Quadtree  # Quadtree is in a separate module


#directory for assets
sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
sprites_dir = os.path.join(os.path.dirname(__file__), 'sprites')



# -------------------------
# Sound Effects & Music
# -------------------------
explosion_sound = pyglet.media.load(os.path.join(sound_dir, "explosion.wav"), streaming=False)
laser_sound = pyglet.media.load(os.path.join(sound_dir, "laserShoot.wav"), streaming=False)
powerup_sound = pyglet.media.load(os.path.join(sound_dir, "powerUp.wav"), streaming=False)
background_music = pyglet.media.load(os.path.join(sound_dir, "background.wav"), streaming=True)
player_bg = background_music.play()
player_bg.loop = True
player_bg.volume = 0.5

# -------------------------
# Images
# -------------------------
from pyglet.image import load
powerup_img = load(os.path.join(sprites_dir ,"powerup.png"))
powerup_img.anchor_x = powerup_img.width // 2
powerup_img.anchor_y = powerup_img.height // 2

astrode_img = load(os.path.join(sprites_dir ,"astrode.png"))
astrode_img.anchor_x = astrode_img.width // 2
astrode_img.anchor_y = astrode_img.height // 2

lazer_img = load(os.path.join(sprites_dir ,"lazer.png"))
lazer_img.anchor_x = lazer_img.width // 2
lazer_img.anchor_y = lazer_img.height // 2

# -------------------------
# Helper Function: Safe Sprite Deletion
# -------------------------
def safe_delete_sprite(sprite):
    if sprite is not None and getattr(sprite, "_vertex_list", None) is not None:
        sprite.delete()

# -------------------------
# Constants for Active Object Limits
# -------------------------
MAX_LASERS = 50
MAX_ASTEROIDS = 90

# -------------------------
# Main Game Class
# -------------------------
class Game(pyglet.window.Window):
    def __init__(self, width=800, height=600):
        super().__init__(width=width, height=height, caption="Astro Shooter")
        self.batch = pyglet.graphics.Batch()

        # Game states: "menu", "playing", "paused", "gameover"
        self.game_state = "menu"
        self.score = 0
        self.lives = 3
        self.high_score = load_high_score()

        # Power-up effects (dictionary-based)
        self.active_powerups = {"speed_boost": 1.0, "tryL_boost": False, "shield": False}
        self.powerup_timers = {"speed_boost": 0.0, "tryL_boost": 0.0, "shield": 0.0}

        # Game object lists
        self.lasers = []
        self.asteroids = []
        self.explosions = []
        self.powerups = []

        # Use a set for active key presses
        self.active_keys = set()

        # Use a quadtree for spatial partitioning
        self.quadtree_boundary = (0, 0, width, height)
        self.quadtree = Quadtree(self.quadtree_boundary)

        # Set player sprite's batch
        player.player_sprite.batch = self.batch

        # Shooting control (old auto-fire behavior)
        self.iamshooting = False
        self.shoottime = 0
        self.shootspeed = 3  # Fire every 3 frames while auto-firing

        # Fixed timestep variables
        self.fixed_dt = 1/60.0
        self.accumulator = 0.0

        # Manual FPS counter
        self.fps = 0
        self.fps_frames = 0
        self.fps_time = 0

        # Create text labels once
        self.label_score = pyglet.text.Label(
            "Score: 0", x=10, y=height - 30, font_size=18, color=(255,255,255,255)
        )
        self.label_lives = pyglet.text.Label(
            "Lives: 3", x=10, y=height - 60, font_size=18, color=(255,255,255,255)
        )
        self.label_fps = pyglet.text.Label(
            "FPS: 0", x=10, y=height - 90, font_size=14, color=(255,255,255,255)
        )
        self.label_menu = pyglet.text.Label(
            "Astro Shooter\nPress ENTER to Start", font_name="Arial", font_size=24,
            x=width//2, y=height//2, anchor_x="center", anchor_y="center",
            color=(255,255,255,255)
        )
        self.label_pause = pyglet.text.Label(
            "PAUSED\nPress P to Resume", font_name="Arial", font_size=32,
            x=width//2, y=height//2, anchor_x="center", anchor_y="center",
            color=(255,255,0,255)
        )
        self.label_gameover_main = pyglet.text.Label(
            "GAME OVER", font_name="Arial", font_size=32,
            x=width//2, y=height//2+40, anchor_x="center", anchor_y="center",
            color=(255,0,0,255)
        )
        self.label_gameover_score = pyglet.text.Label(
            "Final Score: 0", font_name="Arial", font_size=24,
            x=width//2, y=height//2, anchor_x="center", anchor_y="center",
            color=(255,255,255,255)
        )
        self.label_gameover_highscore = pyglet.text.Label(
            "High Score: 0", font_name="Arial", font_size=20,
            x=width//2, y=height//2-40, anchor_x="center", anchor_y="center",
            color=(255,255,255,255)
        )
        self.label_gameover_restart = pyglet.text.Label(
            "Press ENTER to Restart", font_name="Arial", font_size=18,
            x=width//2, y=height//2-80, anchor_x="center", anchor_y="center",
            color=(255,255,255,255)
        )

        # Set mouse cursor
        image = pyglet.image.load(os.path.join(sprites_dir ,"pointer.png"))
        cursor = pyglet.window.ImageMouseCursor(image)
        self.set_mouse_cursor(cursor)

        # Schedule fixed update loop
        pyglet.clock.schedule_interval(self.main_update, self.fixed_dt)

    def main_update(self, dt):
        self.accumulator += dt
        while self.accumulator >= self.fixed_dt:
            self.fixed_update(self.fixed_dt)
            self.accumulator -= self.fixed_dt

        # Update FPS counter
        self.fps_frames += 1
        self.fps_time += dt
        if self.fps_time >= 1.0:
            self.fps = self.fps_frames / self.fps_time
            self.fps_frames = 0
            self.fps_time = 0

    def fixed_update(self, dt):
        if random.randint(0, 100) <= 5:
            gc.collect()

        # Update power-up timers
        for key in self.powerup_timers:
            if self.powerup_timers[key] > 0:
                self.powerup_timers[key] -= dt
                if self.powerup_timers[key] <= 0:
                    if key == "speed_boost":
                        self.active_powerups[key] = 1.0
                    else:
                        self.active_powerups[key] = False

        # If paused, skip updates
        if self.game_state == "paused":
            return

        if self.game_state == "playing":
            # Determine movement from active keys
            direction_vectors = {
                pyglet.window.key.W: (0, 1),
                pyglet.window.key.S: (0, -1),
                pyglet.window.key.A: (-1, 0),
                pyglet.window.key.D: (1, 0)
            }
            dx, dy = 0, 0
            speed = 300 * self.active_powerups.get("speed_boost", 1.0)
            for key in self.active_keys:
                if key in direction_vectors:
                    vx, vy = direction_vectors[key]
                    dx += vx
                    dy += vy
            dx *= speed * dt
            dy *= speed * dt
            player.CheckAndMove(dx, dy, player, 0.7, self.active_powerups.get("speed_boost", 1.0))
            player.PointAndCalculate(player, self)

            # Rebuild quadtree
            self.quadtree = Quadtree(self.quadtree_boundary)
            for l in self.lasers:
                self.quadtree.insert(l, l.lazer_sprite.x, l.lazer_sprite.y)
            for a in self.asteroids:
                self.quadtree.insert(a, a.astrode_sprite.x, a.astrode_sprite.y)

            # Auto-fire: double click auto-fire (fire immediately on press and then every 'shoottime' frames)
            self.shoottime += 1
            if self.iamshooting and self.shoottime == self.shootspeed:
                self.shoottime = 0
                self.shoot(self.active_powerups.get("tryL_boost", False))

            # Update lasers and check collisions using quadtree query
            for l in self.lasers[:]:
                if getattr(l.lazer_sprite, "_vertex_list", None) is None:
                    self.lasers.remove(l)
                    continue
                query_rect = (l.lazer_sprite.x - 50, l.lazer_sprite.y - 50, 100, 100)
                nearby = self.quadtree.query_range(query_rect)
                for a in nearby:
                    if isinstance(a, astrod.astrode) and l.collides_with(a):
                        explosion_sound.play()
                        self.explosions.append(Explosion(a.astrode_sprite.x, a.astrode_sprite.y, self.batch))
                        fragments = a.explode()
                        self.asteroids.extend(fragments)
                        self.score += 50
                        if random.randint(1, 100) <= 5:
                            self.powerups.append(PowerUp(a.astrode_sprite.x, a.astrode_sprite.y, self.batch, powerup_img))
                        safe_delete_sprite(a.astrode_sprite)
                        if a in self.asteroids:
                            self.asteroids.remove(a)
                        safe_delete_sprite(l.lazer_sprite)
                        if l in self.lasers:
                            self.lasers.remove(l)
                        break
                if getattr(l.lazer_sprite, "_vertex_list", None) is not None:
                    l.update(dt)
                else:
                    if l in self.lasers:
                        self.lasers.remove(l)
                    continue
                if l.is_out_of_bounds(self.width, self.height):
                    safe_delete_sprite(l.lazer_sprite)
                    if l in self.lasers:
                        self.lasers.remove(l)
            if len(self.lasers) > MAX_LASERS:
                self.lasers = self.lasers[-MAX_LASERS:]

            # Update asteroids
            for a in self.asteroids[:]:
                a.update(dt)
                if a.is_out_of_bounds(self.width, self.height):
                    safe_delete_sprite(a.astrode_sprite)
                    self.asteroids.remove(a)
                    continue
                dx_a = a.astrode_sprite.x - player.player_sprite.x
                dy_a = a.astrode_sprite.y - player.player_sprite.y
                if dx_a*dx_a + dy_a*dy_a < 900:
                    explosion_sound.play()
                    self.explosions.append(Explosion(a.astrode_sprite.x, a.astrode_sprite.y, self.batch))
                    if not self.active_powerups.get("shield", False):
                        self.lives -= 1
                    safe_delete_sprite(a.astrode_sprite)
                    if a in self.asteroids:
                        self.asteroids.remove(a)
            if len(self.asteroids) > MAX_ASTEROIDS:
                self.asteroids = self.asteroids[-MAX_ASTEROIDS:]

            # Update power-ups
            for pu in self.powerups[:]:
                pu.update(dt)
                if pu.collides_with(player.player_sprite):
                    effect = pu.apply()
                    powerup_sound.play()
                    for key in effect:
                        self.active_powerups[key] = effect[key]
                        dur_key = key + "_duration"
                        if dur_key in effect:
                            self.powerup_timers[key] = effect[dur_key]
                    safe_delete_sprite(pu.sprite)
            self.powerups = [pu for pu in self.powerups if pu.active]

            # Update explosions
            for exp in self.explosions[:]:
                if not exp.update(dt):
                    safe_delete_sprite(exp.sprite)
                    self.explosions.remove(exp)

            # Spawn new asteroids
            if random.randint(0, 100) <= 5:
                self.asteroids.append(astrod.astrode(
                    self.batch,
                    random.randint(0, self.width),
                    random.randint(0, self.height),
                    random.randint(-5, 5)*50,
                    random.randint(-5, 5)*50,
                    random.randint(0,360),
                    random.randint(23,45),
                    0.35,
                    type_val=3,
                    astrode_img=astrode_img
                ))

            # Check for game over
            if self.lives <= 0:
                # Save high score if current score is higher
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
                self.game_state = "gameover"
                self.iamshooting = False
                for l in self.lasers:
                    safe_delete_sprite(l.lazer_sprite)
                self.lasers.clear()
                for a in self.asteroids:
                    safe_delete_sprite(a.astrode_sprite)
                self.asteroids.clear()
                for exp in self.explosions:
                    safe_delete_sprite(exp.sprite)
                self.explosions.clear()
                for pu in self.powerups:
                    safe_delete_sprite(pu.sprite)
                self.powerups.clear()

    def on_draw(self):
        self.clear()
        self.batch.draw()
        if self.game_state == "menu":
            self.label_menu.draw()
        elif self.game_state == "playing":
            self.label_score.text = f"Score: {self.score}"
            self.label_lives.text = f"Lives: {self.lives}"
            self.label_fps.text = f"FPS: {self.fps:.2f}"
            self.label_score.draw()
            self.label_lives.draw()
            self.label_fps.draw()
        elif self.game_state == "paused":
            self.label_pause.draw()
        elif self.game_state == "gameover":
            gc.collect()
            self.label_gameover_main.draw()
            self.label_gameover_score.text = f"Final Score: {self.score}"
            self.label_gameover_score.draw()
            self.label_gameover_highscore.text = f"High Score: {self.high_score}"
            self.label_gameover_highscore.draw()
            self.label_gameover_restart.draw()

    def on_key_press(self, symbol, modifiers):
        self.active_keys.add(symbol)
        if self.game_state == "menu":
            if symbol == pyglet.window.key.ENTER:
                self.start_game()
        elif self.game_state == "playing":
            if symbol == pyglet.window.key.P:
                self.game_state = "paused"
                self.iamshooting = False
                self.shoottime = 0
        elif self.game_state == "paused":
            if symbol == pyglet.window.key.P:
                self.game_state = "playing"
        elif self.game_state == "gameover":
            if symbol == pyglet.window.key.ENTER:
                self.start_game()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.active_keys:
            self.active_keys.discard(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "playing" and button == pyglet.window.mouse.LEFT:
            self.iamshooting = True
            self.shoot(self.active_powerups.get("tryL_boost", False))

    def on_mouse_release(self, x, y, button, modifiers):
        if self.game_state == "playing" and button == pyglet.window.mouse.LEFT:
            self.iamshooting = False
            self.shoottime = 0

    def start_game(self):
        self.game_state = "playing"
        self.score = 0
        self.lives = 3
        self.iamshooting = False
        self.shoottime = 0
        self.active_powerups = {"speed_boost": 1.0, "tryL_boost": False, "shield": False}
        self.powerup_timers = {"speed_boost": 0.0, "tryL_boost": 0.0, "shield": 0.0}
        for l in self.lasers:
            safe_delete_sprite(l.lazer_sprite)
        self.lasers.clear()
        for a in self.asteroids:
            safe_delete_sprite(a.astrode_sprite)
        self.asteroids.clear()
        for exp in self.explosions:
            safe_delete_sprite(exp.sprite)
        self.explosions.clear()
        for pu in self.powerups:
            safe_delete_sprite(pu.sprite)
        self.powerups.clear()
        self.active_keys.clear()

    def shoot(self, tryL_boost):
        if tryL_boost:
            for z in range(-45, 46, 45):
                new_laser = lazer.Lazer(
                    player.player_sprite.x,
                    player.player_sprite.y,
                    player.player_sprite.rotation + z,
                    self.batch,
                    lazer_img
                )
                self.lasers.append(new_laser)
                laser_sound.play()
        else:
            new_laser = lazer.Lazer(
                player.player_sprite.x,
                player.player_sprite.y,
                player.player_sprite.rotation,
                self.batch,
                lazer_img
            )
            self.lasers.append(new_laser)
            laser_sound.play()
        if len(self.lasers) > MAX_LASERS:
            self.lasers = self.lasers[-MAX_LASERS:]

if __name__ == "__main__":
    game = Game(800, 600)
    game.active_keys = set()
    pyglet.app.run()
