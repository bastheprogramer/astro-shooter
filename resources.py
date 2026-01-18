from pathlib import Path
import pyglet
from typing import Dict, Tuple

class ResourceManager:
    """
    Simple ResourceManager that loads images and sounds and returns two dicts:
    - sprites: Dict[str, pyglet.image.AbstractImage]
    - sounds: Dict[str, pyglet.media.Source]
    Public methods use PascalCase (per request).
    """

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)

    def load_image(self, relative_path: str, center_anchor: bool=False) -> pyglet.image.abstract_image:
        p = self.base_path / relative_path
        if not p.exists():
            raise RuntimeError(f'Missing image asset: {p}')
        img = pyglet.image.load(str(p))
        if center_anchor:
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2
        return img

    def load_sound(self, relative_path: str, streaming: bool=False) -> pyglet.media.source:
        p = self.base_path / relative_path
        if not p.exists():
            raise RuntimeError(f'Missing sound asset: {p}')
        return pyglet.media.load(str(p), streaming=streaming)

    def load_resources(self) -> Tuple[Dict[str, pyglet.image.abstract_image], Dict[str, pyglet.media.source]]:
        sprite_dir = self.base_path / 'sprites'
        sound_dir = self.base_path / 'sounds'
        sprites = {'player': self.load_image(sprite_dir / 'player.png', center_anchor=True), 'laser': self.load_image(sprite_dir / 'lazer.png', center_anchor=True), 'asteroid': self.load_image(sprite_dir / 'astrode.png', center_anchor=True), 'explosion': self.load_image(sprite_dir / 'explosion.png', center_anchor=True), 'powerup': self.load_image(sprite_dir / 'powerup.png', center_anchor=True), 'cursor': self.load_image(sprite_dir / 'pointer.png', center_anchor=False)}
        sounds = {'laser': self.load_sound(sound_dir / 'laserShoot.wav', streaming=False), 'explosion': self.load_sound(sound_dir / 'explosion.wav', streaming=False), 'powerup': self.load_sound(sound_dir / 'powerUp.wav', streaming=False), 'music': self.load_sound(sound_dir / 'background.wav', streaming=True)}
        return (sprites, sounds)