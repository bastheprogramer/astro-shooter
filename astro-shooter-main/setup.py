from setuptools import setup

APP = ['main.py']  # Replace with your entry point if different.
DATA_FILES = [
    # Include your assets directories so that images and sounds are bundled.
    ('sprites', ['sprites/player.png', 'sprites/explosion.png', 'sprites/powerup.png', 'sprites/astrode.png', 'sprites/lazer.png', 'sprites/pointer.png']),
    ('sounds', ['sounds/explosion.wav', 'sounds/laserShoot.wav', 'sounds/powerUp.wav', 'sounds/background.wav'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pyglet', 'numpy', 'numba'],
    # You can add other options (like iconfile) if needed.
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
