import pygame
import settings
from scene import Scene


class Logo(Scene):
    def __init__(self, game):
        super().__init__(game)

        # load the title image
        if settings.RESOLUTION == (320, 180):
            self.img_title, _ = self.load_png("dragon-title-180p.png")
        else:
            self.img_title, _ = self.load_png("dragon-title-360p.png")

        # draw a black fade in over the title
        self.fade = pygame.Surface(settings.RESOLUTION)
        self.fade.fill((0, 0, 0))
        self.fade_delay = 0.5
        self.fade_speed = 250
        self.timeout = 3.5

    def update(self):
        if (
            pygame.K_RETURN in self.game.just_pressed
            or pygame.K_SPACE in self.game.just_pressed
            or pygame.K_ESCAPE in self.game.just_pressed
        ):
            self.game.scene_replace = "Starfield"

        if self.elapsed() > self.timeout:
            self.game.scene_replace = "Starfield"

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.img_title, (0, 0))

        # wait to start the fade in from pure black
        if self.elapsed() > self.fade_delay:
            # calculate the fade in
            self.fade.set_alpha(
                255 - min((self.elapsed() - self.fade_delay) * self.fade_speed, 255)
            )

        # start the fade out so it ends at the same time as the timeout of this scene
        if self.elapsed() > self.timeout - 255 / self.fade_speed:
            # calculate the fade out
            self.fade.set_alpha(
                self.constrain(
                    255
                    - (self.timeout - self.elapsed()) / (255 / self.fade_speed) * 255,
                    0,
                    255,
                )
            )
        self.screen.blit(self.fade, (0, 0))
