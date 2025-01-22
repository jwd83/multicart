import pygame
from scene import Scene
from utils import *


class JackNinjasWinner(Scene):
    def __init__(self, game):
        super().__init__(game)

        time_elapsed: float = self.game.jack_ninjas_victory_time

        # turns the time_elapsed float into a string that reads like a clock
        # with minutes and seconds and fractions of a seconds
        time_elapsed_str = " {:02} : {:02} : {:03}".format(
            int(time_elapsed / 60),
            int(time_elapsed % 60),
            int((time_elapsed * 1000) % 1000),
        )

        self.Text(
            text="You Won!",
            pos=(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2),
            anchor="center",
        )

        self.Text(
            text="Time: " + time_elapsed_str,
            pos=(
                self.game.screen.get_width() / 2,
                self.game.screen.get_height() / 2 + 50,
            ),
            anchor="center",
        )

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.TextDraw()
