import pygame
from scene import Scene
from utils import *
from .scripts.qb import QBMode
import settings
import math


class QuadMenu(Scene):
    def __init__(self, game):
        super().__init__(game)

        # default to multiplayer
        self.game.qb_mode = QBMode.Multiplayer

        # menu setup
        self.background, _ = self.load_png("../quadblox/title.png")
        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.standard_font_size = 40
        self.text_choose = self.standard_text("Mode Selection")
        self.standard_font_size = 20
        self.options = [
            self.standard_text("Multiplayer"),
            self.standard_text("40 Line Rush"),
            self.standard_text("Solo Endless"),
            self.standard_text("Leaderboard"),
            self.standard_text("Quit"),
        ]
        self.selected = 0

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed and not settings.WASM:
            self.game.scene_replace = "GameSelect"

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
                self.game.qb_mode = QBMode.Multiplayer
                self.game.scene_replace = ["Plasma", "QuadBlox"]

            elif self.selected == 1:
                self.game.qb_mode = QBMode.SoloForty
                self.game.scene_replace = ["Plasma", "QuadBlox"]

            elif self.selected == 2:
                self.game.qb_mode = QBMode.SoloEndless
                self.game.scene_replace = ["Plasma", "QuadBlox"]

            elif self.selected == 3:
                self.game.scene_replace = "QuadLeaderboard"

    def draw(self):
        # choose a soothing sky blue
        # self.screen.fill((18, 27, 180))
        self.screen.blit(self.background, (0, 0))

        y_spacing = 25
        y_base = 200

        self.blit_centered(self.text_choose, self.screen, (0.5, 0.5))

        for i, option in enumerate(self.options):
            if i == self.selected:
                option.set_alpha(255)
            else:
                option.set_alpha(150)
            self.screen.blit(option, (100, y_base + i * y_spacing))

        self.screen.blit(
            self.img_cursor,
            (50, y_base + self.selected * y_spacing + math.sin(self.elapsed() * 4) * 4),
        )
