import pygame
from scene import Scene
from utils import *
import numpy as np
import math
import settings
from numba import jit, njit

# https://github.com/Apsis/Synthetic-Programming


class Julia(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.standard_font_size = 10
        self.f_text = self.Text("", (10, 10))
        self.update_f()

    def update_f(self):
        t = self.elapsed()
        self.f = math.sin(t)
        self.cx = math.cos(t / 7)
        self.f_text.text = (
            f"t = {t:.4f}, f = sin(t) = {self.f:.4f}, cx = cos(t/7) = {self.cx:.4f}"
        )

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.update_f()

        self.julia_set = generate_julia(
            settings.RESOLUTION[0], settings.RESOLUTION[1], self.f, self.cx
        )

        # Draw the surface on the screen
        draw_julia_set(self.screen, self.julia_set)

        self.TextDraw()


# def draw_julia_set(screen, julia_set):
#     # Convert grayscale to RGB
#     rgb_julia_set = np.stack((julia_set,) * 3, axis=-1)

#     # Convert numpy array to Pygame surface
#     surface = pygame.surfarray.make_surface(rgb_julia_set)

#     # Draw the surface on the screen
#     screen.blit(surface, (0, 0))


@njit
def color_mapping(iteration):
    # Map the iteration count to a color
    # Here we use a simple linear mapping to the RGB color space
    # You can replace this with any function you like
    r = (iteration % 8) * 32
    g = (iteration % 16) * 16
    b = (iteration % 32) * 8
    return (r, g, b)


@njit
def add_color(julia_set):
    # Convert grayscale to RGB
    rgb_julia_set = np.zeros(
        (julia_set.shape[0], julia_set.shape[1], 3), dtype=np.uint8
    )
    for i in range(julia_set.shape[0]):
        for j in range(julia_set.shape[1]):
            rgb_julia_set[i, j] = color_mapping(julia_set[i, j])

    return rgb_julia_set


def draw_julia_set(screen, julia_set):

    rgb_julia_set = add_color(julia_set)

    # Convert numpy array to Pygame surface
    surface = pygame.surfarray.make_surface(rgb_julia_set)

    # Draw the surface on the screen
    screen.blit(surface, (0, 0))


@njit
def generate_julia(h, w, f, cx):

    re_min = -2.0
    re_max = 2.0
    im_min = -2.0
    im_max = 2.0
    c = complex(cx, f)
    real_range = np.arange(re_min, re_max, (re_max - re_min) / w)
    image_range = np.arange(im_max, im_min, (im_min - im_max) / h)
    julia_set = np.zeros((h, w))
    for i, im in enumerate(image_range):
        for j, re in enumerate(real_range):
            z = complex(re, im)
            n = 255
            while abs(z) < 10 and n >= 5:
                z = z * z + c
                n -= 5
            julia_set[i, j] = n

    return julia_set
