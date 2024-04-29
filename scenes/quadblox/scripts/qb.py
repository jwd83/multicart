import random

class Board:
    def __init__(self):
        self.rows = 24
        self.cols = 10
        self.grid = [[random.randint(1,len(colors) - 1) for _ in range(self.cols)] for _ in range(self.rows)]

    def clear(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def reset(self):
        self.clear()
        self.grid = [[random.randint(1,len(colors) - 1) for _ in range(self.cols)] for _ in range(self.rows)]

    def __str__(self):
        return "\n".join("".join(str(cell) for cell in row) for row in self.grid)

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
]