import math
import pygame
import settings
from scene import Scene


class GameSelect(Scene):
    def __init__(self, game):
        super().__init__(game)

        # menu setup

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.standard_font_size = 50
        self.text_multicart = self.standard_text("Jack Games Multicart")
        self.standard_font_size = 40
        self.text_choose = self.standard_text("Choose a game")
        self.options = [
            self.standard_text("4 Jacks"),
            self.standard_text("Via Galactica"),
            self.standard_text("Roguelike"),
            self.standard_text("Font Test"),
            self.standard_text("Quit"),
        ]
        self.selected = 0

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.quit = True

        if pygame.K_DOWN in self.game.just_pressed:
            self.selected = (self.selected + 1) % len(self.options)
            self.play_sound("click")

        if pygame.K_UP in self.game.just_pressed:
            self.selected = (self.selected - 1) % len(self.options)
            self.play_sound("click")

        if pygame.K_RETURN in self.game.just_pressed:
            if self.selected != len(self.options) - 1:
                self.play_sound("jsxfr-select")

            if self.selected == 0:
                self.game.scene_replace = "FourJacksTitle"
            elif self.selected == 1:
                self.game.scene_replace = "ViaStarfield"
            elif self.selected == 2:
                self.game.scene_replace = "Roguelike"
            elif self.selected == 3:
                self.game.scene_replace = "FontTest"
            elif self.selected == 4:
                self.game.quit = True

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.blit_centered(self.text_multicart, self.screen, (0.5, 0.1))
        self.blit_centered(self.text_choose, self.screen, (0.5, 0.2))

        for i, option in enumerate(self.options):
            self.screen.blit(option, (100, 100 + i * 50))

        self.screen.blit(
            self.img_cursor,
            (50, 105 + self.selected * 50 + math.sin(self.elapsed() * 4) * 6),
        )
