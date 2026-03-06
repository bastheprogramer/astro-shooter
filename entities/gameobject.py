import pyglet


class gameobject(pyglet.sprite.Sprite):
    """Common base class for all sprite-based game objects."""

    def __init__(self, img, x, y, batch):
        super().__init__(img, x=x, y=y, batch=batch)
        self.active = True

    def deactivate(self):
        self.active = False

    def is_out_of_bounds(self, width: int, height: int, margin: int = 0) -> bool:
        return (
            self.x < -margin
            or self.x > width + margin
            or self.y < -margin
            or self.y > height + margin
        )

