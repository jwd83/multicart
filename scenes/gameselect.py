import math
import pygame
import settings
from scene import Scene

class GameSelect(Scene):
    def __init__(self, game):
        super().__init__(game)

        # menu setup
        self.background, _ = self.load_png("dall-e-chess-space.png")
        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.standard_font_size = 40
        self.text_multicart = self.standard_text("Jack Games Multicart")
        self.text_choose = self.standard_text("make a selection")
        self.standard_font_size = 20
        self.options = [
            self.standard_text("4 Jacks"),
            self.standard_text("Jack Ninjas"),
            self.standard_text("Jack Ninjas Editor"),
            self.standard_text("Via Galactica"),
            self.standard_text("Jack Wizards"),
            self.standard_text("Superball"),
            self.standard_text("Font Test"),
            self.standard_text("Options"),
            self.standard_text("Quit to Desktop"),
        ]
        self.selected = 0

        # play the default music
        self.play_music("sounds/music.wav")

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed and not settings.WASM:
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
                self.game.scene_replace = "JackNinjasTitle"
            elif self.selected == 2:
                self.game.scene_replace = "JackNinjasEditor"
            elif self.selected == 3:
                self.game.scene_replace = "ViaStarfield"
            elif self.selected == 4:
                self.game.scene_replace = "JackWizards"
            elif self.selected == 5:
                self.game.scene_replace = "SuperBallTitle"
            elif self.selected == 6:
                self.game.scene_replace = "FontTest"
            elif self.selected == 7:
                self.game.scene_push = "Menu"
            elif self.selected == 8 and not settings.WASM:
                self.game.quit = True

    def draw(self):
        # choose a soothing sky blue
        # self.screen.fill((18, 27, 180))
        self.screen.blit(self.background, (0, 0))

        y_spacing = 25

        self.blit_centered(self.text_multicart, self.screen, (0.5, 0.1))
        self.blit_centered(self.text_choose, self.screen, (0.5, 0.2))

        for i, option in enumerate(self.options):
            if i == self.selected:
                option.set_alpha(255)
            else:
                option.set_alpha(150)
            self.screen.blit(option, (100, 100 + i * y_spacing))

        self.screen.blit(
            self.img_cursor,
            (50, 100 + self.selected * y_spacing + math.sin(self.elapsed() * 4) * 4),
        )
