import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    # compute the new normalized vector that will have a fixed length of 1
    def normalize_velocity(self):
        # store the result of the current magnitude at the time of calling
        result = self.magnitude()
        if result != 0:
            self.x /= result
            self.y /= result

    # scale the velocity of the current vector taking the magnitude of the vector into account
    # and using the max_x_or_y_from_origin to scale the velocity of the vector
    def scale_velocity(self):
        max_x_or_y_from_origin = max(abs(self.x), abs(self.y))

        if max_x_or_y_from_origin != 0:

            result = self.magnitude()
            self.x = (self.x / result) * max_x_or_y_from_origin
            self.y = (self.y / result) * max_x_or_y_from_origin

    def pos(self):
        return (self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
