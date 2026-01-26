# Tri-Baller game constants

# Bubble dimensions
BUBBLE_RADIUS = 12
BUBBLE_DIAMETER = BUBBLE_RADIUS * 2

# Grid dimensions
GRID_COLS = 15
GRID_MAX_ROWS = 20

# Playfield dimensions (centered in 640x360)
PLAYFIELD_WIDTH = GRID_COLS * BUBBLE_DIAMETER  # 360px
PLAYFIELD_LEFT = (640 - PLAYFIELD_WIDTH) // 2  # 140px
PLAYFIELD_TOP = 20

# Shooter position
SHOOTER_X = 640 // 2
SHOOTER_Y = 340

# Ball physics
BALL_SPEED = 8

# Aim constraints (in degrees)
AIM_MIN_ANGLE = 10
AIM_MAX_ANGLE = 170

# Vibrant colors for better contrast (indices 1-7 are bubble colors)
# Index 0 is empty, index 8 is white for highlight
COLORS = [
    (0, 0, 0),        # 0 - empty/black
    "#ff4757",        # 1 - red
    "#ff6b35",        # 2 - orange (red-orange)
    "#fff000",        # 3 - yellow (bright yellow)
    "#32cd32",        # 4 - green (lime green)
    "#00bfff",        # 5 - cyan (deep sky blue)
    "#4169e1",        # 6 - blue (royal blue)
    "#a55eea",        # 7 - purple
]

# Number of colors to use (can be adjusted for difficulty)
NUM_COLORS = 7

# Difficulty: shots before ceiling drops
SHOTS_BEFORE_DROP = 8

# Game states
STATE_AIMING = 0
STATE_SHOOTING = 1
STATE_MATCHING = 2
STATE_FALLING = 3
STATE_GAME_OVER = 4
STATE_WIN = 5

# Animation timing (in frames)
MATCH_FLASH_FRAMES = 15
FALL_SHAKE_FRAMES = 10

# Danger line - if bubbles reach this row, game over
DANGER_ROW = 16


def hex_to_rgb(color):
    """Convert hex color string to RGB tuple."""
    if isinstance(color, str) and color.startswith("#"):
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    return color


def get_color(index):
    """Get RGB color tuple for a given color index."""
    if 0 <= index < len(COLORS):
        return hex_to_rgb(COLORS[index])
    return (0, 0, 0)
