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
        self.mouse_hide = True

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.standard_font_size = 40
        self.text_multicart = self.standard_text("Jack Games Multicart")
        self.text_choose = self.standard_text("make a selection")
        self.standard_font_size = 15

        self.opts = {
            "GeometryBlast": "Geometry Blast",
            "RayCaster": "Ray Caster",
            "JackNinjasTitle": "Jack Ninjas",
            "JackNinjasEditor": "Jack Ninjas Editor",
            "JackBlackJackTitle": "Blackjack",
            "Solitaire": "Solitaire",
            "TriBaller": "Tri-Baller",
            "QuadMenu": "QuadBlox",
            "FourJacksTitle": "Four Jacks",
            "JackWizards": "Jack Wizards",
            "JackDefenseTitle": "JackTD",
            "ViaTitle": "Via Galactica",
            "Golden": "Test: Golden",
            "MultiTest": "Test: Multi",
            "Warp": "Test: Warp",
            "Julia": "Test: Julia",
            "FontTest": "Test: Font",
            "Menu": "Menu",
            "Quit": "Quit to Desktop",
        }

        self.texts = {}

        for opt in self.opts:
            self.texts[opt] = self.standard_text(self.opts[opt])

        self.selected = 0

        # play the default music
        self.play_music("sounds/music.wav")

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed and not settings.WASM:
            self.game.quit = True

        if pygame.K_DOWN in self.game.just_pressed:
            self.selected = (self.selected + 1) % len(self.opts)
            self.play_sound("click")

        if pygame.K_UP in self.game.just_pressed:
            self.selected = (self.selected - 1) % len(self.opts)
            self.play_sound("click")

        if pygame.K_RETURN in self.game.just_pressed:
            if self.selected != len(self.opts) - 1:
                self.play_sound("jsxfr-select")

            selected_op = 0
            for opt in self.opts:
                if selected_op == self.selected:
                    if opt == "Quit":
                        self.game.quit = True
                    elif opt == "Menu":
                        self.game.scene_push = "Menu"
                    else:
                        self.game.scene_replace = opt
                selected_op += 1

    def draw(self):
        y_spacing = self.standard_font_size + 5

        i = 0
        for txt in self.texts:
            if i == self.selected:
                self.texts[txt].set_alpha(255)
            else:
                self.texts[txt].set_alpha(150)

            y_offset = 0
            if self.selected >= 5:
                y_offset = (self.selected - 4) * y_spacing

            self.screen.blit(self.texts[txt], (100, 100 + i * y_spacing - y_offset))
            i += 1

        self.screen.blit(
            self.img_cursor,
            (
                50,
                100
                + self.selected * y_spacing
                - y_offset
                + math.sin(self.elapsed() * 4) * 4,
            ),
        )

        self.blit_centered(self.text_multicart, self.screen, (0.5, 0.1))
        self.blit_centered(self.text_choose, self.screen, (0.5, 0.2))
        self.draw_mouse()
