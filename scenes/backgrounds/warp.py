import pygame
from scene import Scene
from utils import *
import settings


class Star:
    def __init__(self):
        self.x = random.randint(-settings.WIDTH, settings.WIDTH)
        self.y = random.randint(-settings.HEIGHT, settings.HEIGHT)
        self.z = random.randint(0, settings.WIDTH)
        self.pz = self.z

    def update(self, speed):
        self.z -= speed
        if self.z < 1:
            self.x = random.randint(-settings.WIDTH, settings.WIDTH)
            self.y = random.randint(-settings.HEIGHT, settings.HEIGHT)
            self.z = settings.WIDTH
            self.pz = self.z

    def draw(self, screen):
        sx = (
            int(interpolate(self.x / self.z, 0, 1, 0, settings.WIDTH) + settings.WIDTH)
            // 2
        )
        sy = (
            int(
                interpolate(self.y / self.z, 0, 1, 0, settings.HEIGHT) + settings.HEIGHT
            )
            // 2
        )

        r = int(interpolate(self.z, 0, settings.WIDTH, 6, 0))

        px = (
            int(interpolate(self.x / self.pz, 0, 1, 0, settings.WIDTH) + settings.WIDTH)
            // 2
        )
        py = (
            int(
                interpolate(self.y / self.pz, 0, 1, 0, settings.HEIGHT)
                + settings.HEIGHT
            )
            // 2
        )

        self.pz = self.z

        # draw trail
        pygame.draw.line(screen, (255, 255, 255), (px, py), (sx, sy), 1)

        # draw star
        # pygame.draw.circle(screen, (255, 255, 255), (sx, sy), r)


class Warp(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.stars = []
        for _ in range(800):
            self.stars.append(Star())

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        mouse_x, mouse_y = pygame.mouse.get_pos()
        speed = interpolate(mouse_x, 0, settings.WIDTH, 0, 50)
        for star in self.stars:
            star.update(speed)

    def draw(self):
        self.screen.fill((0, 0, 0))
        for star in self.stars:
            star.draw(self.screen)
