import pygame
from scene import Scene
from utils import *
import numpy as np
import time
import settings
import threading


class Plasma(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.w = settings.RESOLUTION[0]
        self.h = settings.RESOLUTION[1]

        self.draw_a = True

        self.drawing = False

        # make 2 frames to switch between, one to be drawing on and one to be displaying
        self.frame_a = pygame.Surface((self.w, self.h))
        self.frame_b = pygame.Surface((self.w, self.h))

    def update(self):

        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        if not self.drawing:
            self.drawing = True
            threading.Thread(target=self.draw_v2).start()

        if self.draw_a:
            self.screen.blit(self.frame_a, (0, 0))
        else:
            self.screen.blit(self.frame_b, (0, 0))

    def draw_v1(self):

        # Create 2D arrays for the x and y coordinates
        x, y = np.meshgrid(np.arange(self.h), np.arange(self.w))

        # Get the current time
        t = time.time()

        # Calculate the noise values
        # noise = np.cos(x / 16 + t) + np.cos(y / 16 + t)

        # Calculate the noise values (better?)
        noise = (
            np.cos(x / 16 + t)
            + np.sin(y / 16 + t)
            + np.cos((x + y) / 16 + 2 * t) / 2
            + np.sin(np.sqrt((x - self.w / 2) ** 2 + (y - self.h / 2) ** 2) / 8 + t) / 2
        )

        # Normalize the noise values to the range [0, 1]
        noise = ((noise + 2) / 4 * 255).astype(np.uint8)

        # Create an empty array for the pixel colors
        pixels = np.zeros((self.w, self.h, 3), dtype=np.uint8)

        # Set the red and blue components of the colors
        pixels[..., 0] = noise  #
        pixels[..., 2] = 255 - noise  # Blue

        # Convert the pixel array to a Pygame surface and blit it to the screen
        image = pygame.surfarray.make_surface(pixels)

        # update the frame we are not currently drawing
        if self.draw_a:
            self.frame_b.blit(image, (0, 0))
        else:
            self.frame_a.blit(image, (0, 0))

        self.draw_a = not self.draw_a
        self.drawing = False

    def draw_v2(self):

        width, height = self.game.screen.get_size()

        # Create 2D arrays for the x and y coordinates
        x, y = np.meshgrid(np.arange(height), np.arange(width))

        # Get the current time
        t = time.time()

        # Calculate the noise values for red and blue
        noise_rb = (
            np.cos(x / 16 + t)
            + np.sin(y / 16 + t)
            + np.cos((x + y) / 16 + 2 * t) / 2
            + np.sin(np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2) / 8 + t) / 2
        )

        # Calculate the noise values for green
        noise_g = (
            np.cos(x / 16 + t / 2)
            + np.sin(y / 16 + t / 2)
            + np.cos((x + y) / 16 + t) / 2
            + np.sin(np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2) / 8 + t / 2)
            / 2
        )

        # Normalize the noise values to the range [0, 1]
        noise_rb = ((noise_rb + 2) / 4 * 255).astype(np.uint8)
        noise_g = ((noise_g + 2) / 4 * 255).astype(np.uint8)

        # Create an empty array for the pixel colors
        pixels = np.zeros((width, height, 3), dtype=np.uint8)

        # Set the red, green and blue components of the colors
        pixels[..., 0] = noise_rb  # Red
        pixels[..., 1] = noise_g  # Green
        pixels[..., 2] = 255 - noise_rb  # Blue

        # Convert the pixel array to a Pygame surface and blit it to the screen
        image = pygame.surfarray.make_surface(pixels)

        # update the frame we are not currently drawing
        if self.draw_a:
            self.frame_b.blit(image, (0, 0))
        else:
            self.frame_a.blit(image, (0, 0))

        self.draw_a = not self.draw_a
        self.drawing = False
