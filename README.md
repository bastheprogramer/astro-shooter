# Astro Shooter

Arcade-style space shooter built with Python and Pyglet. Pilot a ship, destroy incoming asteroids, collect power-ups, unlock stronger weapons, and push for a higher score each run.

## Features

- Fast arcade gameplay with mouse aiming and WASD movement
- Asteroids that split into smaller fragments when destroyed
- Two weapons: laser and tracking missile
- Power-ups for extra lives, score boosts, faster firing, movement speed, and split shots
- Pause, game over, and restart flow
- Persistent high score saved locally
- Debug mode with FPS, TPS, entity count, spawn rate, and memory usage

## Requirements

- Python 3.10+
- A desktop environment capable of running Pyglet windows and audio

## Installation

1. Clone the repository:

```bash
git clone https://github.com/bastheprogramer/astro-shooter.git
cd astro-shooter
```

2. Install dependencies:

```bash
make install
```

If you prefer `pip` directly:

```bash
pip install -r requirements.txt
```

## Run

Start the game with:

```bash
make
```

Or run Python directly:

```bash
python main.py
```

## Controls

- `W`, `A`, `S`, `D`: Move
- Mouse: Aim
- Left click: Fire
- `Enter`: Start or restart
- `Esc`: Pause or resume
- `1`, `2`: Switch unlocked weapons
- `P`: Toggle debug mode
- `O`: Toggle auto mode while debug mode is enabled

## Gameplay Notes

- You begin with 3 lives.
- Asteroid pressure increases as your score rises.
- Tracking missiles unlock after reaching a score threshold.
- Power-ups drop randomly from destroyed hostiles.
- High scores are stored in `~/.astro_shooter/highscore.txt`.

## Project Structure

- [main.py](main.py): Main game loop and window logic
- [entities/](entities): Player, weapons, asteroids, power-ups, and effects
- [resources.py](resources.py): Asset loading and playback
- [Scheduler.py](Scheduler.py): Delayed game actions
- [highscore.py](highscore.py): Local high score persistence

## Possible Next Additions

- Wave-based progression and boss encounters
- More enemy types with distinct movement patterns
- Expanded weapon roster
- Combo scoring and leaderboards
- Better menu and settings screens

## Credits

- Developed by [bastheprogramer](https://github.com/bastheprogramer)
