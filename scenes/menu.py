import math
import pygame
import settings
from scene import Scene


class Menu(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.selected = 0

        self.create_text()

    def create_text(self):

        self.standard_font_size = 40
        self.standard_color = (255, 255, 255)
        self.standard_stroke_color = (0, 0, 0)
        self.standard_stroke_thickness = 2
        self.standard_stroke = True

        self.options = [
            self.standard_text("sfx . . . " + str(self.game.volume_effects)),
            self.standard_text("music . . " + str(self.game.volume_music)),
            self.standard_text("window/fullscreen"),
            self.standard_text("return to multicart"),
            self.standard_text("quit to desktop"),
        ]

        # make text for the options menu
        self.text_options = self.make_text(
            text="options",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

    def update(self):

        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_pop = True

        if pygame.K_LEFT in self.game.just_pressed:
            if self.selected == 0:
                self.game.volume_effects = (self.game.volume_effects - 10) % 110
                self.create_text()
            if self.selected == 1:
                self.game.volume_music = (self.game.volume_music - 10) % 110
                self.create_text()

        if pygame.K_RIGHT in self.game.just_pressed:
            if self.selected == 0:
                self.game.volume_effects = (self.game.volume_effects + 10) % 110
                self.create_text()
            if self.selected == 1:
                self.game.volume_music = (self.game.volume_music + 10) % 110
                self.create_text()

        if pygame.K_RETURN in self.game.just_pressed:

            if self.selected == 0:
                self.game.volume_effects = (self.game.volume_effects + 10) % 110
                self.create_text()
            if self.selected == 1:
                self.game.volume_music = (self.game.volume_music + 10) % 110

                self.create_text()
            if self.selected == 2 and not settings.WASM:
                self.log("toggle fullscreen")
                self.game.fullscreen = not self.game.fullscreen
                pygame.display.toggle_fullscreen()
            if self.selected == 3:
                self.play_sound("jsxfr-select")
                self.game.scene_replace = "GameSelect"
            if self.selected == 4 and not settings.WASM:
                self.game.quit = True

        if pygame.K_UP in self.game.just_pressed:
            self.selected = (self.selected - 1) % len(self.options)
            self.play_sound("click")

        if pygame.K_DOWN in self.game.just_pressed:
            self.selected = (self.selected + 1) % len(self.options)
            self.play_sound("click")

    def draw(self):
        self.draw_box(
            (40, 50), (settings.RESOLUTION[0] - 120, settings.RESOLUTION[1] - 70)
        )

        # wait for the box to finish drawing before drawing the text
        if self.elapsed() < self.box_delay:
            return

        self.blit_centered(self.text_options, self.screen, (0.5, 0.2))

        y_spacing = 45
        for i, option in enumerate(self.options):
            if i == self.selected:
                option.set_alpha(255)
            else:
                option.set_alpha(150)

            self.screen.blit(option, (100, 100 + i * y_spacing))

        self.screen.blit(
            self.img_cursor,
            (50, 105 + self.selected * y_spacing + math.sin(self.elapsed() * 4) * 6),
        )
