import math
import pygame
import settings
from scene import Scene


class GameSelect(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.game.scene_push_under = "Plasma"

        # menu setup
        self.background, _ = self.load_png("dall-e-chess-space.png")

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.standard_font_size = 40
        self.text_multicart = self.standard_text("Jack Games Multicart")
        self.text_choose = self.standard_text("make a selection")
        self.standard_font_size = 15
        self.options = [
            self.standard_text("QuadBlox"),
            self.standard_text("Jack Ninjas"),
            self.standard_text("Jack Ninjas Editor"),
            self.standard_text("Jack Wizards"),
            self.standard_text("Julia"),
            self.standard_text("Golden"),
            self.standard_text("JackTD"),
            self.standard_text("Blackjack"),
            self.standard_text("Multi Test"),
            self.standard_text("Warp"),
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
                self.game.scene_replace = "QuadMenu"
            elif self.selected == 1:
                self.game.scene_replace = "JackNinjasTitle"
            elif self.selected == 2:
                self.game.scene_replace = "JackNinjasEditor"
            elif self.selected == 3:
                self.game.scene_replace = "JackWizards"
            elif self.selected == 4:
                self.game.scene_replace = "Julia"
            elif self.selected == 5:
                self.game.scene_replace = "Golden"
            elif self.selected == 6:
                self.game.scene_replace = "JackDefenseTitle"
            elif self.selected == 7:
                self.game.scene_replace = "JackBlackJackTitle"
            elif self.selected == 8:
                self.game.scene_replace = "MultiTest"
            elif self.selected == 9:
                self.game.scene_push = "Warp"
            elif self.selected == 10:
                self.game.scene_push = "Menu"
            elif self.selected == 11 and not settings.WASM:
                self.game.quit = True

    def draw(self):
        # choose a soothing sky blue
        # self.screen.fill((18, 27, 180))
        # self.screen.blit(self.background, (0, 0))

        y_spacing = self.standard_font_size + 5

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
