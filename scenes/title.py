import scene
import pygame
import settings


class Title(scene.Scene):
    def __init__(self, game):
        super().__init__(game)
        # make text of the game
        self.text_via = self.make_text(
            text="via",
            color=(255, 0, 255),
            fontSize=180,
            stroke=True,
            strokeColor=(255, 255, 255),
            strokeThickness=3,
        )
        self.text_galactica = self.make_text(
            text="galactica",
            color=(255, 255, 255),
            fontSize=60,
            stroke=True,
            strokeColor=(100, 100, 255),
            strokeThickness=2,
        )
        self.text_road = self.make_text(
            text="the road of",
            color=(255, 0, 255),
            fontSize=50,
            stroke=True,
            strokeColor=(255, 255, 255),
            strokeThickness=2,
        )
        self.text_milk = self.make_text(
            text="milk",
            color=(255, 255, 255),
            fontSize=128,
            stroke=True,
            strokeColor=(100, 100, 255),
            strokeThickness=3,
        )

        self.text_press_enter = self.make_text(
            text="press enter to start",
            color=(255, 255, 255),
            fontSize=30,
            stroke=True,
            strokeColor=(255, 0, 0),
            strokeThickness=2,
        )

        # load the title_ship.png image
        self.img_ship, self.img_ship_rect = self.load_png("title_ship.png")

        # resize to 1/4 of the original size
        self.img_ship = pygame.transform.scale(
            self.img_ship,
            (
                int(self.img_ship_rect.width / 4),
                int(self.img_ship_rect.height / 4),
            ),
        )

        # update the rect
        self.img_ship_rect = self.img_ship.get_rect()

    def update(self):
        # if escape was pressed quit the game
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.quit = True

        # if enter was pressed start the game
        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_pop = True
            self.game.scene_push = "Level"

    def draw(self):
        progress = self.constrain(self.elapsed() / 1, 0, 1)

        # draw the ship coming in from the top right
        self.img_ship_rect.topleft = (
            settings.RESOLUTION[0] - self.img_ship_rect.width * progress,
            -self.img_ship_rect.height + self.img_ship_rect.height * progress,
        )
        self.screen.blit(self.img_ship, self.img_ship_rect)

        self.blit_centered(
            source=self.text_galactica,
            target=self.screen,
            position=(0.5, progress * 0.42),
        )
        self.blit_centered(
            source=self.text_via, target=self.screen, position=(progress * 0.5, 0.2)
        )

        self.blit_centered(
            source=self.text_road,
            target=self.screen,
            position=(1 - progress * 0.5, 0.55),
        )
        self.blit_centered(
            source=self.text_milk,
            target=self.screen,
            position=(0.5, 0.7 + (1 - progress) * 0.5),
        )

        if progress >= 1:

            self.blit_centered(
                source=self.text_press_enter, target=self.screen, position=(0.5, 0.9)
            )
