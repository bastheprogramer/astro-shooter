from pathlib import Path
from typing import Dict, Tuple, Union
import numpy as np
from Weapons import WeaponType
import pyglet


class AssetRegistry:
    """Central registry for loaded sprites and sounds."""

    def __init__(
        self,
        sprites: Dict[str, pyglet.image.AbstractImage],
        sounds: Dict[str, pyglet.media.Source],
    ) -> None:
        self._sprites = dict(sprites)
        self._sounds = dict(sounds)


    @property
    def sprites(self) -> Dict[str, pyglet.image.AbstractImage]:
        return self._sprites

    @property
    def sounds(self) -> Dict[str, pyglet.media.Source]:
        return self._sounds

    def sprite(self, key: str) -> pyglet.image.AbstractImage:
        return self._sprites[key]

    def sound(self, key: str) -> pyglet.media.Source:
        return self._sounds[key]

    def play(self, key: str) -> None:
        try:
            self.sound(key).play()
        except:
            print(f"error on playing sound {key}")


class resource_manager:
    """
    Simple ResourceManager that loads images and sounds and returns a registry:
    - sprites: Dict[str, pyglet.image.AbstractImage]
    - sounds: Dict[str, pyglet.media.Source]
    """

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)

    def load_image(
        self,
        relative_path: Union[str, Path],
        center_anchor: bool = False,
    ) -> pyglet.image.AbstractImage:
        p = self.base_path / relative_path
        if not p.exists():
            raise RuntimeError(f'Missing image asset: {p}')
        img = pyglet.image.load(str(p))
        if center_anchor:
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2
        return img

    def load_sound(
        self,
        relative_path: Union[str, Path],
        streaming: bool = False,
    ) -> pyglet.media.Source:
        p = self.base_path / relative_path
        if not p.exists():
            raise RuntimeError(f'Missing sound asset: {p}')
        return pyglet.media.load(str(p), streaming=streaming)

    def load_resources(self) -> AssetRegistry:
        sprite_dir = self.base_path / 'sprites'
        sound_dir = self.base_path / 'sounds'
        sprites = {
            'player': self.load_image(sprite_dir / 'player.png', center_anchor=True),
            WeaponType.laser.value: self.load_image(sprite_dir / 'laser.png', center_anchor=True),
            'asteroid': self.load_image(sprite_dir / 'astrode.png', center_anchor=True),
            'explosion': self.load_image(sprite_dir / 'explosion.png', center_anchor=True),
            'powerup': self.load_image(sprite_dir / 'powerup.png', center_anchor=True),
            'cursor': self.load_image(sprite_dir / 'pointer.png', center_anchor=False),
            WeaponType.tracking_missile.value: self.load_image(sprite_dir / 'missile.png', center_anchor=True),
        }
        sounds = {
            WeaponType.laser.value: self.load_sound(sound_dir / 'laserShoot.wav', streaming=False),
            'explosion': self.load_sound(sound_dir / 'explosion.wav', streaming=False),
            'powerup': self.load_sound(sound_dir / 'powerUp.wav', streaming=False),
            'music': self.load_sound(sound_dir / 'background.wav', streaming=True),
            WeaponType.tracking_missile.value: self.load_sound(sound_dir / 'missile.wav', streaming=False),
        }
        return AssetRegistry(sprites, sounds)

