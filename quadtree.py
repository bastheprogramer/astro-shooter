# quadtree.py

class Quadtree:
    def __init__(self, boundary, capacity=4, level=0, max_level=5):
        self.boundary = boundary  # (x, y, width, height)
        self.capacity = capacity
        self.level = level
        self.max_level = max_level
        self.objects = []  # List of tuples: (object, x, y)
        self.divided = False

    def subdivide(self):
        x, y, w, h = self.boundary
        hw, hh = w / 2, h / 2
        self.northeast = Quadtree((x + hw, y + hh, hw, hh), self.capacity, self.level + 1, self.max_level)
        self.northwest = Quadtree((x, y + hh, hw, hh), self.capacity, self.level + 1, self.max_level)
        self.southeast = Quadtree((x + hw, y, hw, hh), self.capacity, self.level + 1, self.max_level)
        self.southwest = Quadtree((x, y, hw, hh), self.capacity, self.level + 1, self.max_level)
        self.divided = True

    def insert(self, obj, x, y):
        bx, by, bw, bh = self.boundary
        if not (bx <= x < bx + bw and by <= y < by + bh):
            return False
        if len(self.objects) < self.capacity or self.level >= self.max_level:
            self.objects.append((obj, x, y))
            return True
        if not self.divided:
            self.subdivide()
        if self.northeast.insert(obj, x, y):
            return True
        if self.northwest.insert(obj, x, y):
            return True
        if self.southeast.insert(obj, x, y):
            return True
        if self.southwest.insert(obj, x, y):
            return True
        return False

    def query_range(self, range_rect, found=None):
        # range_rect: (x, y, width, height)
        if found is None:
            found = []
        if not self.intersects(self.boundary, range_rect):
            return found
        for (obj, ox, oy) in self.objects:
            if self.point_in_rect((ox, oy), range_rect):
                found.append(obj)
        if self.divided:
            self.northeast.query_range(range_rect, found)
            self.northwest.query_range(range_rect, found)
            self.southeast.query_range(range_rect, found)
            self.southwest.query_range(range_rect, found)
        return found

    @staticmethod
    def intersects(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax > bx + bw or ax + aw < bx or ay > by + bh or ay + ah < by)

    @staticmethod
    def point_in_rect(point, rect):
        x, y = point
        rx, ry, rw, rh = rect
        return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)
