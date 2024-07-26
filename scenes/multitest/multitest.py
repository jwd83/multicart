import pygame
from scene import Scene
from utils import *
from classes.animatedsprite import AnimatedSprite
from classes.animation import Animation


class MultiTest(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.a_s = AnimatedSprite(
            {
                "idle": Animation("assets/jackninjas/images/entities/player/idle/"),
                "fall": Animation("assets/jackninjas/images/entities/player/fall/"),
                "jump": Animation("assets/jackninjas/images/entities/player/jump/"),
                "run": Animation("assets/jackninjas/images/entities/player/run/"),
                "slide": Animation("assets/jackninjas/images/entities/player/slide/"),
                "wall_slide": Animation(
                    "assets/jackninjas/images/entities/player/wall_slide/"
                ),
            },
            100,
            100,
        )

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_TAB in self.game.just_pressed:
            # make a list of the animations
            animations = list(self.a_s.animations.keys())
            # select a random one

            self.a_s.change_animation(random.choice(animations))

        self.a_s.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.a_s.draw(self.screen)
