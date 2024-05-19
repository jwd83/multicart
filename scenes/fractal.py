import pygame
from scene import Scene
from utils import *
import settings
from PIL import Image
import numpy as np


class Fractal(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.texts = {}
        self.texts["title"] = self.Text(
            "Fractal",
            (settings.RESOLUTION[0] // 2, settings.RESOLUTION[1] // 2),
            "center",
        )
        self.x1 = -2
        self.y1 = -2
        self.x2 = 2
        self.y2 = 2
        self.render_fractal()

        self.box_start = False
        self.left_click = 0

    def render_fractal(self):
        pil_image = Image.effect_mandelbrot(
            (640, 360), (self.x1, self.y1, self.x2, self.y2), 200
        )
        print(pil_image)
        pil_image = pil_image.convert("RGB")
        image_data = pil_image.tobytes()
        image_dimensions = pil_image.size

        self.pygame_surface = pygame.image.fromstring(
            image_data, image_dimensions, "RGB"
        )

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        self.mouse_clicks = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

        if self.mouse_clicks[0]:
            self.left_click += 1
        else:
            self.left_click = 0

        if self.mouse_clicks[0] and self.left_click == 1:
            if not self.box_start:
                self.box_start = self.mouse_pos
            else:
                self.x1 = np.interp(
                    self.box_start[0],
                    [0, settings.RESOLUTION[0]],
                    [self.x1, self.x2],
                )
                self.y1 = np.interp(
                    self.box_start[1],
                    [0, settings.RESOLUTION[1]],
                    [self.y1, self.y2],
                )
                self.x2 = np.interp(
                    self.mouse_pos[0],
                    [0, settings.RESOLUTION[0]],
                    [self.x1, self.x2],
                )
                self.y2 = np.interp(
                    self.mouse_pos[1],
                    [0, settings.RESOLUTION[1]],
                    [self.y1, self.y2],
                )

                self.render_fractal()
                self.box_start = False

        # # zoom in on where the user clicked
        # if pygame.MOUSEBUTTONDOWN in self.game.just_pressed:
        #     x, y = pygame.mouse.get_pos()

        #     x = np.interp(x, [0, settings.RESOLUTION[0]], [self.x1, self.x2])
        #     y = np.interp(y, [0, settings.RESOLUTION[1]], [self.y1, self.y2])
        #     self.x1 = x - 0.5
        #     self.y1 = y - 0.5
        #     self.x2 = x + 0.5
        #     self.y2 = y + 0.5

        #     self.render_fractal()

        # self.x1 *= 0.985
        # self.y1 *= 0.99
        # self.x2 *= 0.998
        # self.y2 *= 0.99

        # self.render_fractal()

    def draw(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.pygame_surface, (0, 0))

        if self.box_start:
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (
                    self.box_start,
                    (
                        self.mouse_pos[0] - self.box_start[0],
                        self.mouse_pos[1] - self.box_start[1],
                    ),
                ),
                1,
            )
