import pygame
from scene import Scene
from utils import *
import numpy as np
import settings


class Golden(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.turn_step = 0.1  # np.sqrt(2)  # square root of two
        self.circle_radius = 4
        self.place_distance = 10
        self.circles = []
        self.text_step = self.Text(f"{self.turn_step}", (10, 10))

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))

        center = (settings.RESOLUTION[0] // 2, settings.RESOLUTION[1] // 2)

        self.circles = []

        self.turn_angle = 0

        for i in range(200):
            # start the circle at the center facing 90 degrees to the right down the x axis
            x_step = np.cos(self.turn_angle) * self.place_distance
            y_step = np.sin(self.turn_angle) * self.place_distance

            # num_steps = 1 + (self.turn_angle // (np.pi * 2))
            num_steps = 1
            # self.log(f"num_steps: {num_steps}")

            x = center[0] + x_step * num_steps
            y = center[1] + y_step * num_steps

            # check if we collide with any other circles
            for circle in self.circles:
                # move us away from the circle if we collide by our step amount
                if self.distance((x, y), circle) < self.circle_radius * 2:
                    x += x_step
                    y += y_step

            # # add the circle to the list of circles
            self.circles.append((x, y))

            # increment the angle
            self.turn_angle += self.turn_step * (np.pi * 2)

        # draw the circles
        for i, circle in enumerate(self.circles):
            pygame.draw.circle(
                self.screen,
                (255 - i, i, 150),
                (int(circle[0]), int(circle[1])),
                self.circle_radius,
            )

        self.turn_step += 0.0001
        self.text_step.text = f"{self.turn_step}"

        self.TextDraw()

    def distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
