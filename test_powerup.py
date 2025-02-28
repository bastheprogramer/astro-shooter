# tests/test_powerup.py
import pyglet
from powerup import PowerUp

def test_apply_returns_dict():
    
    # Instantiate PowerUp with dummy parameters.
    # The PowerUp constructor requires: x, y, batch, image, and optionally ptype.
    # For testing, we can pass:
    #  - x and y as 0,
    #  - batch as None (if your code tolerates it in a test environment),
    #  - dummy_img for the image,
    #  - ptype as "life" (or any valid type) for consistency.
    powerup_instance = PowerUp()
    
    # Call the apply method; it should return an effect dictionary.
    result = powerup_instance.apply()
    
    # Check that the result is a dictionary.
    assert isinstance(result, dict), f"Expected a dict, got {type(result)}"
