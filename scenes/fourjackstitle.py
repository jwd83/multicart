import pygame
from scene import Scene
import random
import math


class FourJacksTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.img_cursor, _ = self.load_png("opengameart-hand_cursor0000.png")
        self.positions = [(0.03, 0.49), (0.2, 0.64), (0.2, 0.74)]

        self.selected_position = 0
        self.selected_ai_color = 1

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((80, 120, 190))

        # make up our text
        text_title = self.make_text("4Jacks!", (30, 30, 30), 8 * 8)
        text_hot_seat = self.make_text("Play vs Local Hot Seat", (50, 50, 50), 8 * 3)
        text_ai = self.make_text("Play vs AI", (50, 50, 50), 8 * 3)
        text_quit = self.make_text(
            text="[Esc] to Quit", color=(80, 80, 80), fontSize=8 * 3
        )

        self.text_ai_color = []
        self.text_ai_color.append(self.make_text("AI Color: Red   ", "RED", 8 * 2))
        self.text_ai_color.append(self.make_text("AI Color: Yellow", "YELLOW", 8 * 2))
        self.text_ai_color.append(self.make_text("AI Color: Random", "ORANGE", 8 * 2))

        # write the static text to the background
        self.blit_centered(text_title, self.background, (0.5, 0.2))
        self.blit_centered(text_hot_seat, self.background)
        self.blit_centered(text_ai, self.background, (0.5, 0.65))
        self.blit_centered(text_quit, self.background, (0.5, 0.9))

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "GameSelect"
            return

        if (
            pygame.K_SPACE in self.game.just_pressed
            or pygame.K_RETURN in self.game.just_pressed
        ):
            self.play_sound("jsxfr-select")
            # starting at the top option, start the game in hotseat mode
            if self.selected_position == 0:
                self.game.four_jacks_ai = None
                self.game.scene_push = "FourJacksGameBoard"

            # if the user selects the second option, set the game to hotseat mode and start it
            if self.selected_position == 1:
                if self.selected_ai_color == 2:
                    self.game.four_jacks_ai = random.choice([0, 1])
                else:
                    self.game.four_jacks_ai = self.selected_ai_color
                self.game.scene_push = "FourJacksGameBoard"

            # if the user selects the third option, change the AI color setting
            if self.selected_position == 2:
                self.selected_ai_color += 1
                self.selected_ai_color %= len(self.text_ai_color)

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
            # draw the background
            self.screen.blit(self.background, (0, 0))

            # draw the dynamic text for ai color to the screen
            self.blit_centered(
                self.text_ai_color[self.selected_ai_color], self.screen, (0.5, 0.74)
            )

            # draw the cursor
            self.blit_centered(
                self.img_cursor,
                self.screen,
                (
                    self.positions[self.selected_position][0],
                    self.positions[self.selected_position][1]
                    + 0.015 * math.sin(self.elapsed() * 4),
                ),
            )
