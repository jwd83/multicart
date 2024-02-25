import pygame
import settings
from scene import Scene


class FontTest(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.test_strings = []

        for i in range(20, 200, 20):
            print("Making text with size", i)
            self.test_strings.append(
                self.make_text(
                    text="Font Size " + str(i),
                    color=(255, 255, 255),
                    fontSize=i,
                    stroke=True,
                    strokeColor=(0, 0, 0),
                    strokeThickness=2,
                )
            )

        print(self.test_strings)

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):

        self.screen.fill((127, 127, 127))
        print(self.test_strings)

        y = 0
        step = 20
        for str_to_draw in self.test_strings:
            self.screen.blit(str_to_draw, (0, int(y)))
            y += step
            step += 20
