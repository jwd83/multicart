import pygame
from scene import Scene
from utils import *
import settings
from PIL import Image


class Fractal(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.texts = {}
        self.texts["title"] = self.Text(
            "Fractal",
            (settings.RESOLUTION[0] // 2, settings.RESOLUTION[1] // 2),
            "center",
        )
        self.x1 = -3
        self.y1 = -2.5
        self.x2 = 2
        self.y2 = 2.5
        self.render_fractal()

    def render_fractal(self):
        pil_image = Image.effect_mandelbrot(
            (640, 360), (self.x1, self.y1, self.x2, self.y2), 100
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

        self.x1 *= 0.99
        self.y1 *= 0.99
        self.x2 *= 0.99
        self.y2 *= 0.99

        self.render_fractal()

    def draw(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.pygame_surface, (0, 0))
