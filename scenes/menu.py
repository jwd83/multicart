import pygame
import settings
from scene import Scene


class Menu(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.create_text()
        self.img_cursor, _ = self.load_png("cursor-4x7.png")
        self.play_sound("click")

        self.option_selected = 0
        self.option_count = 4

    def create_text(self):

        # make text for the options menu
        self.text_options = self.make_text(
            text="options",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

        self.text_return_to_title = self.make_text(
            text="return to title",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

        self.text_quit = self.make_text(
            text="quit to desktop",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

        self.text_volume_sfx = self.make_text(
            text="sfx",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

        self.text_volume_music = self.make_text(
            text="music",
            color=(255, 255, 255),
            fontSize=40,
            stroke=True,
            strokeColor=(0, 0, 0),
            strokeThickness=2,
        )

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_pop = True

        if pygame.K_RETURN in self.game.just_pressed:
            self.play_sound("click")
            if self.option_selected == 0:
                pass
            if self.option_selected == 1:
                pass
            if self.option_selected == 2:
                self.game.scene_pop = 2
                self.game.scene_push = "Title"

            if self.option_selected == 3:
                self.game.quit = True

        if pygame.K_UP in self.game.just_pressed:
            self.option_selected -= 1
            self.play_sound("click")

        if pygame.K_DOWN in self.game.just_pressed:
            self.option_selected += 1
            self.play_sound("click")

        self.option_selected = self.option_selected % self.option_count

    def draw(self):
        self.draw_box(
            (100, 50), (settings.RESOLUTION[0] - 200, settings.RESOLUTION[1] - 100)
        )
        if self.elapsed() > self.box_delay:

            self.blit_centered(self.text_options, self.screen, (0.5, 0.2))

            self.screen.blit(self.text_volume_sfx, (125, 100))
            self.screen.blit(self.text_volume_music, (125, 150))
            self.screen.blit(self.text_return_to_title, (125, 200))
            self.screen.blit(self.text_quit, (125, 250))
            self.screen.blit(self.img_cursor, (110, 120 + 50 * self.option_selected))
