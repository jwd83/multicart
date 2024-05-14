import pygame
from scene import Scene
from utils import *
import numpy as np
import time


class Plasma(Scene):
    def __init__(self, game):
        super().__init__(game)

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        width, height = self.game.screen.get_size()

        # Create 2D arrays for the x and y coordinates
        x, y = np.meshgrid(np.arange(height), np.arange(width))

        # Get the current time
        t = time.time()

        # Calculate the noise values
        noise = np.cos(x / 16 + t) + np.cos(y / 16 + t)

        # Normalize the noise values to the range [0, 1]
        noise = ((noise + 2) / 4 * 255).astype(np.uint8)

        # Create an empty array for the pixel colors
        pixels = np.zeros((width, height, 3), dtype=np.uint8)

        # Set the red and blue components of the colors
        pixels[..., 0] = noise  # Red
        pixels[..., 2] = 255 - noise  # Blue

        # Convert the pixel array to a Pygame surface and blit it to the screen
        image = pygame.surfarray.make_surface(pixels)
        self.game.screen.blit(image, (0, 0))
