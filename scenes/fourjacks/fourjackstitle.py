import pygame
from scene import Scene
import random
import math
import settings


class FourJacksTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.background = self.make_transparent_surface(self.screen.get_size())
        self.background_image, _ = self.load_png("dalle-4jacks.png")
        self.background_image.set_alpha(125)  # make it not so bright
        self.background.blit(self.background_image, (0, 0))

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.positions = [100, 140, 180, 220, 260, 300]

        self.selected_position = 0
        self.selected_ai_color = 2

        # self.background = pygame.Surface(self.screen.get_size())
        # self.background = self.background.convert()
        # self.background.fill((80, 120, 190))

        # make up our text
        self.standard_stroke_color = "BLACK"
        self.standard_font_size = 80
        self.standard_stroke_thickness = 4
        text_title = self.standard_text("4Jacks!")

        self.standard_font_size = 40
        self.standard_stroke_thickness = 2
        text_hot_seat = self.standard_text("Play Local Hot Seat")
        text_ai = self.standard_text("Play vs AI Easy")
        text_ai_hard = self.standard_text("Play vs AI Hard")
        text_return = self.standard_text(text="return to multicart")
        text_quit = self.standard_text("Quit")

        self.text_ai_color = []
        self.standard_color = "RED"
        self.text_ai_color.append(self.standard_text("AI Color: Red"))
        self.standard_color = "YELLOW"
        self.text_ai_color.append(self.standard_text("AI Color: Yellow"))
        self.standard_color = "ORANGE"
        self.text_ai_color.append(self.standard_text("AI Color: Random"))

        # write the static text to the background
        self.blit_centered(text_title, self.background, (0.5, 0.15))

        self.background.blit(text_hot_seat, (100, 100))
        self.background.blit(text_ai, (100, 140))
        self.background.blit(text_ai_hard, (100, 180))
        self.background.blit(text_return, (100, 260))
        self.background.blit(text_quit, (100, 300))

    def handle_selection(self):
        # starting at the top option, start the game in hotseat mode
        if self.selected_position == 0:
            self.game.four_jacks_ai = None
            self.game.scene_push = "FourJacksGameBoard"

        # if the user selects the second option, set the game to vs ai easy
        if self.selected_position == 1:
            self.game.four_jacks_easy = True
            if self.selected_ai_color == 2:
                self.game.four_jacks_ai = random.choice([0, 1])
            else:
                self.game.four_jacks_ai = self.selected_ai_color
            self.game.scene_push = "FourJacksGameBoard"

        # if the user selects the third option, set the game to vs ai hard
        if self.selected_position == 2:
            self.game.four_jacks_easy = False

            if self.selected_ai_color == 2:
                self.game.four_jacks_ai = random.choice([0, 1])
            else:
                self.game.four_jacks_ai = self.selected_ai_color
            self.game.scene_push = "FourJacksGameBoard"

        # if the user selects the fourth option, change the AI color setting
        if self.selected_position == 3:
            self.selected_ai_color += 1
            self.selected_ai_color %= len(self.text_ai_color)

        # if the user selects the fifth option, return to the multicart
        if self.selected_position == 4:
            self.game.scene_replace = "GameSelect"
            return

        # if the user selects the sixth option, quit the game
        if self.selected_position == 5 and not settings.WASM:
            self.game.quit = True

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "GameSelect"
            return

        if (
            pygame.K_SPACE in self.game.just_pressed
            or pygame.K_RETURN in self.game.just_pressed
        ):
            if self.selected_position != 5:
                self.play_sound("jsxfr-select")
            self.handle_selection()

        if (
            pygame.K_LEFT in self.game.just_pressed
            or pygame.K_UP in self.game.just_pressed
        ):
            self.play_sound("click")

            self.selected_position -= 1
            self.selected_position %= len(self.positions)
        if (
            pygame.K_RIGHT in self.game.just_pressed
            or pygame.K_DOWN in self.game.just_pressed
        ):
            self.play_sound("click")
            self.selected_position += 1
            self.selected_position %= len(self.positions)

    def draw(self):
        if self.active:
            # draw a black background
            self.screen.fill((0, 0, 0))

            # draw the background
            self.screen.blit(self.background, (0, 0))

            # draw the dynamic text for ai color to the screen
            self.screen.blit(self.text_ai_color[self.selected_ai_color], (100, 220))

            # draw the cursor
            self.screen.blit(
                self.img_cursor,
                (
                    50,
                    10
                    + self.positions[self.selected_position]
                    + math.sin(self.elapsed() * 4) * 6,
                ),
            )
