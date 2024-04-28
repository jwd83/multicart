class Board:
    def __init__(self):
        self.rows = 30
        self.cols = 10
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

