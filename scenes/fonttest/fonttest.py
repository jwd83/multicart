import pygame
import settings
from scene import Scene


class FontTest(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.test_strings = []

        for i in [20, 40, 60, 80, 100, 120, 140]:
            self.log(f"Making text with size {i}")
            self.test_strings.append(
                self.make_text(
                    text=str(i) + ": .,;?! the quick brown fox jumps over the lazy dog",
                    color=(255, 255, 255),
                    fontSize=i,
                    stroke=True,
                    strokeColor=(0, 0, 0),
                    strokeThickness=2,
                )
            )

    def update(self):
        if (
            (pygame.K_ESCAPE in self.game.just_pressed)
            or (pygame.K_SPACE in self.game.just_pressed)
            or (pygame.K_RETURN in self.game.just_pressed)
        ):
            self.game.scene_push = "Menu"

    def draw(self):

        self.screen.fill((127, 127, 127))

        y = 0
        step = 11
        for str_to_draw in self.test_strings:
            self.screen.blit(str_to_draw, (0, int(y)))
            y += step
            step += 11
