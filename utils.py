import math
import numpy as np
from typing import List, Tuple, Union, Dict
from pyglet.image import AbstractImage

MaskCache: Dict[int, np.ndarray] = {}
def create_alpha_mask(image):
    raw = image.get_image_data()
    data = raw.get_data('RGBA', raw.width * 4)
    array = np.frombuffer(data, dtype=np.uint8)
    array = array.reshape((raw.height, raw.width, 4))
    return array[:, :, 3] > 0

def check_circle_collision(sprite_a, sprite_b):
    # A rotation-safe quick distance check. 
    # Calculates a generous radius based on the sprite's largest dimension.
    radius_a = max(sprite_a.width, sprite_a.height) / 2.0
    radius_b = max(sprite_b.width, sprite_b.height) / 2.0
    
    dx = sprite_a.x - sprite_b.x
    dy = sprite_a.y - sprite_b.y
    dist_sq = dx*dx + dy*dy
    
    # Check if the distance between centers is less than combined radii
    return dist_sq <= (radius_a + radius_b)**2

def local_to_world(sprite, lx, ly):
    # 1. Shift by the anchor point
    lx -= sprite.image.anchor_x
    ly -= sprite.image.anchor_y
    
    # 2. Apply clockwise rotation (Pyglet's standard)
    angle = math.radians(sprite.rotation)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    wx = lx * cos_a + ly * sin_a
    wy = -lx * sin_a + ly * cos_a
    
    # 3. Translate to world position
    return wx + sprite.x, wy + sprite.y

def world_to_local(sprite, x, y):
    # 1. Translate to origin
    dx = x - sprite.x
    dy = y - sprite.y

    # 2. Undo clockwise rotation (Rotate counter-clockwise)
    angle = math.radians(sprite.rotation)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Correct math for Counter-Clockwise rotation matrix
    local_x = dx * cos_a - dy * sin_a
    local_y = dx * sin_a + dy * cos_a

    # 3. Add anchor back
    local_x += sprite.image.anchor_x
    local_y += sprite.image.anchor_y

    return int(local_x), int(local_y)

def are_sprites_colliding(sprite_a, sprite_b) -> bool:
    # 1. Fast distance check (Keep your check_circle_collision function)
    if not check_circle_collision(sprite_a, sprite_b):
        return False

    if id(sprite_a.image) not in MaskCache:
        MaskCache[id(sprite_a.image)] = create_alpha_mask(sprite_a.image)

    if id(sprite_b.image) not in MaskCache:
        MaskCache[id(sprite_b.image)] = create_alpha_mask(sprite_b.image)

    mask_a = MaskCache[id(sprite_a.image)]
    mask_b = MaskCache[id(sprite_b.image)]

    

    # 2. Get all local coordinates where Sprite A has solid pixels
    ys, xs = np.nonzero(mask_a)
    
    if len(xs) == 0:  # Safety check if sprite is fully transparent
        return False

    # --- 3. Vectorized Local to World (Sprite A) ---
    lx = (xs - sprite_a.image.anchor_x) * sprite_a.scale_x
    ly = (ys - sprite_a.image.anchor_y) * sprite_a.scale_y
    
    rad_a = -math.radians(sprite_a.rotation)
    cr_a, sr_a = math.cos(rad_a), math.sin(rad_a)
    
    wx = lx * cr_a - ly * sr_a + sprite_a.x
    wy = lx * sr_a + ly * cr_a + sprite_a.y

    # --- 4. Vectorized World to Local (Sprite B) ---
    dx = wx - sprite_b.x
    dy = wy - sprite_b.y
    
    rad_b = math.radians(sprite_b.rotation)
    cr_b, sr_b = math.cos(rad_b), math.sin(rad_b)
    
    bx = dx * cr_b - dy * sr_b
    by = dx * sr_b + dy * cr_b
    
    bx /= (sprite_b.scale_x if sprite_b.scale_x != 0 else 1)
    by /= (sprite_b.scale_y if sprite_b.scale_y != 0 else 1)
    
    # Round to nearest pixel and convert to integer indices
    bx = np.round(bx + sprite_b.image.anchor_x).astype(int)
    by = np.round(by + sprite_b.image.anchor_y).astype(int)

    # --- 5. Vectorized Bounds Check & Collision ---
    # Create a boolean array of points that fall within Sprite B's image bounds
    valid = (bx >= 0) & (bx < mask_b.shape[1]) & (by >= 0) & (by < mask_b.shape[0])
    
    # Check if ANY of those valid points hit a solid pixel in Sprite B's mask
    # This evaluates the entire array instantly
    return bool(np.any(mask_b[by[valid], bx[valid]]))