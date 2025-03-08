from pyglet.image import load
from pyglet.sprite import Sprite
from numba import njit
from numpy import degrees, atan2
import os

sprites_dir = os.path.join(os.path.dirname(__file__), 'sprites')
player_img = load(os.path.join(sprites_dir, "player.png"))
player_img.anchor_x = player_img.width // 2
player_img.anchor_y = player_img.height // 2

player_sprite = Sprite(player_img)
player_sprite.scale = 0.1
player_sprite.x = 400
player_sprite.y = 300

xspeed = 0
yspeed = 0
@njit
def calculate(player_x, player_y, mouse_x, mouse_y):
    dx = player_x - mouse_x
    dy = player_y - mouse_y
    return -(degrees(atan2(dy, dx)))

def PointAndCalculate(player, GameWindow):
    player.player_sprite.rotation = calculate(player_sprite.x, player_sprite.y, GameWindow._mouse_x, GameWindow._mouse_y) - 90

def CheckAndMove(dx, dy, player ,drag, speed_multiplier=1.0):
    # Simply update the player's sprite position using the computed delta values.
    player.xspeed += dx
    player.yspeed += dy
    
    player.xspeed *= drag
    player.yspeed *= drag
    player.player_sprite.x += player.xspeed
    player.player_sprite.y += player.yspeed
