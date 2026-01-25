# Tri-Baller - HexBoard class for grid logic, matching, and connectivity

import random
from collections import deque
from .constants import (
    BUBBLE_RADIUS, BUBBLE_DIAMETER, GRID_COLS, GRID_MAX_ROWS,
    PLAYFIELD_LEFT, PLAYFIELD_TOP, NUM_COLORS, DANGER_ROW
)


class HexBoard:
    """Manages the bubble grid with hex-style offset for odd rows."""

    def __init__(self):
        # grid[row][col] = 0 for empty, 1-7 for colored bubble
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_MAX_ROWS)]
        self.colors_in_play = set()

    def clear(self):
        """Clear the entire grid."""
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_MAX_ROWS)]
        self.colors_in_play = set()

    def grid_to_screen(self, row, col):
        """Convert grid position to screen pixel center."""
        x = PLAYFIELD_LEFT + col * BUBBLE_DIAMETER + BUBBLE_RADIUS
        # Odd rows are offset by half a bubble width
        if row % 2 == 1:
            x += BUBBLE_RADIUS
        y = PLAYFIELD_TOP + row * BUBBLE_DIAMETER + BUBBLE_RADIUS
        return (x, y)

    def screen_to_grid(self, x, y):
        """Find nearest valid grid position for screen coordinates."""
        # Calculate approximate row
        row = int((y - PLAYFIELD_TOP) / BUBBLE_DIAMETER)
        row = max(0, min(row, GRID_MAX_ROWS - 1))

        # Account for odd row offset when calculating column
        adjusted_x = x - PLAYFIELD_LEFT
        if row % 2 == 1:
            adjusted_x -= BUBBLE_RADIUS

        col = int(adjusted_x / BUBBLE_DIAMETER)

        # For odd rows, max col is one less due to offset
        max_col = GRID_COLS - 2 if row % 2 == 1 else GRID_COLS - 1
        col = max(0, min(col, max_col))

        return (row, col)

    def is_valid_position(self, row, col):
        """Check if a grid position is valid."""
        if row < 0 or row >= GRID_MAX_ROWS:
            return False
        max_col = GRID_COLS - 2 if row % 2 == 1 else GRID_COLS - 1
        return 0 <= col <= max_col

    def get_neighbors(self, row, col):
        """Return list of 6 neighboring positions (hex grid)."""
        neighbors = []

        if row % 2 == 0:
            # Even row neighbors
            offsets = [
                (-1, -1), (-1, 0),   # top-left, top-right
                (0, -1), (0, 1),     # left, right
                (1, -1), (1, 0)      # bottom-left, bottom-right
            ]
        else:
            # Odd row neighbors (shifted right)
            offsets = [
                (-1, 0), (-1, 1),    # top-left, top-right
                (0, -1), (0, 1),     # left, right
                (1, 0), (1, 1)       # bottom-left, bottom-right
            ]

        for dr, dc in offsets:
            nr, nc = row + dr, col + dc
            if self.is_valid_position(nr, nc):
                neighbors.append((nr, nc))

        return neighbors

    def get_bubble(self, row, col):
        """Get bubble color at position, 0 if empty or invalid."""
        if not self.is_valid_position(row, col):
            return 0
        return self.grid[row][col]

    def set_bubble(self, row, col, color):
        """Set bubble at position."""
        if self.is_valid_position(row, col):
            self.grid[row][col] = color
            if color > 0:
                self.colors_in_play.add(color)

    def find_connected_same_color(self, row, col):
        """BFS flood-fill to find all connected bubbles of the same color."""
        color = self.get_bubble(row, col)
        if color == 0:
            return []

        visited = set()
        connected = []
        queue = deque([(row, col)])

        while queue:
            r, c = queue.popleft()
            if (r, c) in visited:
                continue
            if self.get_bubble(r, c) != color:
                continue

            visited.add((r, c))
            connected.append((r, c))

            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in visited and self.get_bubble(nr, nc) == color:
                    queue.append((nr, nc))

        return connected

    def find_connected_to_ceiling(self):
        """BFS from row 0 to find all bubbles connected to the ceiling."""
        connected = set()
        queue = deque()

        # Start from all bubbles in row 0
        for col in range(GRID_COLS):
            if self.get_bubble(0, col) > 0:
                queue.append((0, col))
                connected.add((0, col))

        while queue:
            r, c = queue.popleft()

            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in connected and self.get_bubble(nr, nc) > 0:
                    connected.add((nr, nc))
                    queue.append((nr, nc))

        return connected

    def find_floating_bubbles(self):
        """Find all bubbles not connected to the ceiling."""
        connected_to_ceiling = self.find_connected_to_ceiling()
        floating = []

        for row in range(GRID_MAX_ROWS):
            max_col = GRID_COLS - 1 if row % 2 == 0 else GRID_COLS - 2
            for col in range(max_col + 1):
                if self.get_bubble(row, col) > 0:
                    if (row, col) not in connected_to_ceiling:
                        floating.append((row, col))

        return floating

    def remove_bubbles(self, positions):
        """Remove bubbles at given positions."""
        for row, col in positions:
            self.grid[row][col] = 0
        self._update_colors_in_play()

    def _update_colors_in_play(self):
        """Update the set of colors currently on the board."""
        self.colors_in_play = set()
        for row in range(GRID_MAX_ROWS):
            for col in range(GRID_COLS):
                color = self.grid[row][col]
                if color > 0:
                    self.colors_in_play.add(color)

    def generate_level(self, num_rows, num_colors=None):
        """Generate a random starting pattern with given number of rows."""
        if num_colors is None:
            num_colors = NUM_COLORS

        self.clear()
        colors = list(range(1, num_colors + 1))

        for row in range(num_rows):
            max_col = GRID_COLS - 1 if row % 2 == 0 else GRID_COLS - 2
            for col in range(max_col + 1):
                self.grid[row][col] = random.choice(colors)
                self.colors_in_play.add(self.grid[row][col])

    def add_row_at_top(self, num_colors=None):
        """Push all bubbles down and add a new row at the top."""
        if num_colors is None:
            num_colors = NUM_COLORS

        # Shift all rows down
        for row in range(GRID_MAX_ROWS - 1, 0, -1):
            for col in range(GRID_COLS):
                self.grid[row][col] = self.grid[row - 1][col]

        # Generate new top row
        colors = list(range(1, num_colors + 1))
        max_col = GRID_COLS - 1  # Row 0 is even
        for col in range(max_col + 1):
            self.grid[0][col] = random.choice(colors)

        self._update_colors_in_play()

    def is_empty(self):
        """Check if the board is completely empty."""
        for row in range(GRID_MAX_ROWS):
            for col in range(GRID_COLS):
                if self.grid[row][col] > 0:
                    return False
        return True

    def check_game_over(self):
        """Check if any bubbles have reached the danger zone."""
        for col in range(GRID_COLS):
            if self.get_bubble(DANGER_ROW, col) > 0:
                return True
        return False

    def get_random_color_in_play(self):
        """Get a random color that exists on the board."""
        if not self.colors_in_play:
            return random.randint(1, NUM_COLORS)
        return random.choice(list(self.colors_in_play))

    def find_snap_position(self, x, y):
        """Find the best grid position to snap a bubble at screen position."""
        row, col = self.screen_to_grid(x, y)

        # If the position is occupied, find the nearest empty position
        if self.get_bubble(row, col) != 0:
            # Check neighbors for empty spots
            best_pos = None
            best_dist = float('inf')

            for nr, nc in self.get_neighbors(row, col):
                if self.get_bubble(nr, nc) == 0:
                    sx, sy = self.grid_to_screen(nr, nc)
                    dist = (x - sx) ** 2 + (y - sy) ** 2
                    if dist < best_dist:
                        best_dist = dist
                        best_pos = (nr, nc)

            if best_pos:
                return best_pos

        return (row, col)
