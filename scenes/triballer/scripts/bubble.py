# Tri-Baller - FlyingBubble and BubbleParticle classes

import pygame
import math
import random
from .constants import (
    BUBBLE_RADIUS, BALL_SPEED, PLAYFIELD_LEFT, PLAYFIELD_WIDTH,
    PLAYFIELD_TOP, get_color
)


class FlyingBubble:
    """A bubble currently flying through the air after being shot."""

    def __init__(self, x, y, angle, color):
        """
        Initialize a flying bubble.

        Args:
            x, y: Starting position (center of bubble)
            angle: Angle in degrees (0 = right, 90 = up, 180 = left)
            color: Color index (1-7)
        """
        self.x = x
        self.y = y
        self.color = color

        # Convert angle to velocity
        rad = math.radians(angle)
        self.vx = math.cos(rad) * BALL_SPEED
        self.vy = -math.sin(rad) * BALL_SPEED  # Negative because y increases downward

    def update(self):
        """Move the bubble and handle wall bounces."""
        self.x += self.vx
        self.y += self.vy

        # Bounce off left wall
        left_bound = PLAYFIELD_LEFT + BUBBLE_RADIUS
        if self.x < left_bound:
            self.x = left_bound
            self.vx = -self.vx

        # Bounce off right wall
        right_bound = PLAYFIELD_LEFT + PLAYFIELD_WIDTH - BUBBLE_RADIUS
        if self.x > right_bound:
            self.x = right_bound
            self.vx = -self.vx

    def hit_ceiling(self):
        """Check if bubble has hit the ceiling."""
        return self.y - BUBBLE_RADIUS <= PLAYFIELD_TOP

    def draw(self, screen):
        """Draw the bubble with a highlight."""
        color = get_color(self.color)

        # Draw main bubble
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), BUBBLE_RADIUS)

        # Draw highlight (small white circle offset up-left)
        highlight_color = (255, 255, 255)
        highlight_radius = BUBBLE_RADIUS // 3
        highlight_offset = BUBBLE_RADIUS // 3
        pygame.draw.circle(
            screen,
            highlight_color,
            (int(self.x - highlight_offset), int(self.y - highlight_offset)),
            highlight_radius
        )

        # Draw subtle outline
        pygame.draw.circle(
            screen,
            (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40)),
            (int(self.x), int(self.y)),
            BUBBLE_RADIUS,
            1
        )


class BubbleParticle(pygame.sprite.Sprite):
    """Particle effect for popping or falling bubbles."""

    def __init__(self, x, y, color, mode="pop"):
        """
        Initialize a bubble particle.

        Args:
            x, y: Starting position
            color: Color index
            mode: "pop" for explosion effect, "fall" for gravity fall
        """
        super().__init__()

        self.mode = mode
        self.color = get_color(color)
        self.alpha = 255

        # Create the particle image
        size = BUBBLE_RADIUS * 2 if mode == "pop" else BUBBLE_RADIUS
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color + (self.alpha,), (size // 2, size // 2), size // 2)

        self.rect = self.image.get_rect(center=(x, y))

        if mode == "pop":
            # Explosion outward
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.fade_rate = random.randint(8, 15)
        else:
            # Falling with gravity
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(0, 2)
            self.gravity = 0.3
            self.fade_rate = random.randint(4, 8)

    def update(self):
        """Update particle position and alpha."""
        # Move particle
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.mode == "fall":
            self.vy += self.gravity

        # Fade out
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.kill()
            return

        # Update image alpha
        size = self.image.get_width()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            self.color + (max(0, int(self.alpha)),),
            (size // 2, size // 2),
            size // 2
        )
