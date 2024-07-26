# our animated sprite class
# this class is a subclass of the sprite class

import pygame

from .animation import Animation

# the type for a dictionary of animations is : dict[str, Animation]


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(
        self, animations: dict[str, Animation], x, y, start_animation: str | None = None
    ):
        # pygame doesn't let us use super so instead we call...
        pygame.sprite.Sprite.__init__(self)
        self.animations = animations
        if start_animation is None:
            start_animation = list(animations.keys())[0]
        self.current_animation = self.animations[start_animation]
        self.image = self.current_animation.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.current_animation.update()
        self.image = self.current_animation.image

    def change_animation(self, animation_name: str, reset_animation: bool = True):
        self.current_animation = self.animations[animation_name]
        if reset_animation:
            self.current_animation.reset()
        self.image = self.current_animation.image

    def reset(self):
        self.current_animation.reset()
        self.image = self.current_animation.image

    def done(self):
        return self.current_animation.done

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
