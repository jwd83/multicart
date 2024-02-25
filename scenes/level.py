import pygame
import settings
from scene import Scene
import entity


class Level(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = entity.Entity(self)
        self.player_speed = 5

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        self.update_player_movement()

    def update_player_movement(self):

        self.player.velocity.x = 0
        self.player.velocity.y = 0

        if self.game.pressed[pygame.K_LEFT]:
            self.player.velocity.x += -self.player_speed

        if self.game.pressed[pygame.K_RIGHT]:
            self.player.velocity.x += self.player_speed

        if self.game.pressed[pygame.K_UP]:
            self.player.velocity.y += -self.player_speed

        if self.game.pressed[pygame.K_DOWN]:
            self.player.velocity.y += self.player_speed

        self.player.velocity.scale_velocity()

        self.player.position += self.player.velocity
        if self.player.position.x < 0:
            self.player.position.x = 0

        if (
            self.player.position.x
            > settings.RESOLUTION[0] - self.player.sprite.get_width()
        ):
            self.player.position.x = (
                settings.RESOLUTION[0] - self.player.sprite.get_width()
            )

        if self.player.position.y < 0:
            self.player.position.y = 0

        if (
            self.player.position.y
            > settings.RESOLUTION[1] - self.player.sprite.get_height()
        ):
            self.player.position.y = (
                settings.RESOLUTION[1] - self.player.sprite.get_height()
            )

    def draw(self):
        self.player.draw()
