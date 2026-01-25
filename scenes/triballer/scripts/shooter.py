# Tri-Baller - Shooter/launcher with aiming

import pygame
import math
import random
from .constants import (
    SHOOTER_X, SHOOTER_Y, BUBBLE_RADIUS, AIM_MIN_ANGLE, AIM_MAX_ANGLE,
    PLAYFIELD_LEFT, PLAYFIELD_WIDTH, get_color
)


class Shooter:
    """The bubble launcher at the bottom of the screen."""

    def __init__(self, board):
        self.x = SHOOTER_X
        self.y = SHOOTER_Y
        self.angle = 90  # Pointing straight up
        self.board = board

        # Current and next bubble colors
        self.current_color = self._get_new_color()
        self.next_color = self._get_new_color()

    def _get_new_color(self):
        """Get a new bubble color (preferring colors on the board)."""
        return self.board.get_random_color_in_play()

    def aim_at(self, mouse_x, mouse_y):
        """Update aim angle based on mouse position."""
        dx = mouse_x - self.x
        dy = self.y - mouse_y  # Inverted because y increases downward

        if dy <= 0:
            # Mouse is below or at shooter level, aim horizontal
            self.angle = AIM_MIN_ANGLE if dx > 0 else AIM_MAX_ANGLE
            return

        # Calculate angle in degrees
        self.angle = math.degrees(math.atan2(dy, dx))

        # Clamp to valid range
        self.angle = max(AIM_MIN_ANGLE, min(AIM_MAX_ANGLE, self.angle))

    def swap_bubbles(self):
        """Swap current and next bubble colors."""
        self.current_color, self.next_color = self.next_color, self.current_color

    def shoot(self):
        """Return parameters for creating a flying bubble, then load next bubble."""
        color = self.current_color
        angle = self.angle

        # Load next bubble
        self.current_color = self.next_color
        self.next_color = self._get_new_color()

        return (self.x, self.y - BUBBLE_RADIUS - 5, angle, color)

    def refresh_colors(self):
        """Refresh colors to match what's on the board (call after bubbles removed)."""
        if self.current_color not in self.board.colors_in_play and self.board.colors_in_play:
            self.current_color = self._get_new_color()
        if self.next_color not in self.board.colors_in_play and self.board.colors_in_play:
            self.next_color = self._get_new_color()

    def draw(self, screen):
        """Draw the shooter, aim line, current bubble, and next bubble preview."""
        # Draw aim line (dotted)
        rad = math.radians(self.angle)
        line_length = 300

        # Draw dotted line
        num_dots = 20
        for i in range(num_dots):
            t = i / num_dots
            dot_x = self.x + math.cos(rad) * line_length * t
            dot_y = self.y - math.sin(rad) * line_length * t

            # Check bounds
            if dot_x < PLAYFIELD_LEFT or dot_x > PLAYFIELD_LEFT + PLAYFIELD_WIDTH:
                break
            if dot_y < 0:
                break

            if i % 2 == 0:
                pygame.draw.circle(screen, (100, 100, 100), (int(dot_x), int(dot_y)), 2)

        # Draw launcher base
        base_color = (80, 80, 100)
        pygame.draw.rect(
            screen,
            base_color,
            (self.x - 25, self.y - 5, 50, 20),
            border_radius=5
        )

        # Draw current bubble in launcher
        current_bubble_color = get_color(self.current_color)
        bubble_y = self.y - BUBBLE_RADIUS - 5
        pygame.draw.circle(screen, current_bubble_color, (self.x, bubble_y), BUBBLE_RADIUS)

        # Highlight on current bubble
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (self.x - BUBBLE_RADIUS // 3, bubble_y - BUBBLE_RADIUS // 3),
            BUBBLE_RADIUS // 3
        )

        # Draw next bubble preview (smaller, to the right)
        next_x = self.x + 50
        next_y = self.y - 5
        next_radius = BUBBLE_RADIUS - 4
        next_color = get_color(self.next_color)
        pygame.draw.circle(screen, next_color, (next_x, next_y), next_radius)
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (next_x - next_radius // 3, next_y - next_radius // 3),
            next_radius // 3
        )

        # Draw "NEXT" label
        font = pygame.font.Font(None, 16)
        label = font.render("NEXT", True, (200, 200, 200))
        screen.blit(label, (next_x - 14, next_y + next_radius + 2))
