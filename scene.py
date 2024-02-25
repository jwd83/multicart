import time
import math
import pygame
import settings
import os


class Scene:
    def __init__(self, game):
        self.game = game
        self.active = True
        self.screen: pygame.Surface = game.screen
        self.start = time.time()
        self.shadow_intensity = 100
        self.shadow_depth = 3
        self.box_delay = 0.25

    def elapsed(self):
        return time.time() - self.start

    def constrain(self, n, n_min, n_max):
        return max(min(n_max, n), n_min)

    def update(self):
        print("Scene's update method has not been implemented")

    def draw(self):
        # the values of sin range from -1 to 1
        r = math.sin(time.time() * 1.33 + 1.5) * 127 + 128
        g = math.sin(time.time()) * 127 + 128
        b = math.sin(time.time() * 0.25 - 0.6666) * 127 + 128
        self.screen.fill((r, g, b))
        print("Scene's draw method has not been implemented")

    def draw_box(self, position: tuple, size: tuple):
        if self.elapsed() < self.box_delay:
            # expand the box from it's center to it's full size
            position = (
                position[0] + size[0] / 2 * (1 - self.elapsed() / self.box_delay),
                position[1] + size[1] / 2 * (1 - self.elapsed() / self.box_delay),
            )

            size = (
                size[0] * self.elapsed() / self.box_delay,
                size[1] * self.elapsed() / self.box_delay,
            )

            # draw the blue background
            pygame.draw.rect(
                self.game.screen,
                (0, 0, 255),
                (position[0], position[1], size[0], size[1]),
                width=0,
            )

            # draw the white border
            pygame.draw.rect(
                self.game.screen,
                (255, 255, 255),
                (position[0], position[1], size[0], size[1]),
                width=2,
            )
            return

        # create a drop shadow for the box

        for i in range(1, self.shadow_depth + 1):
            self.draw_rect_alpha(
                self.game.screen,
                (0, 0, 0, self.shadow_intensity),
                (position[0] + i, position[1] + i, size[0], size[1]),
            )

        # draw the blue background
        pygame.draw.rect(
            self.game.screen,
            (0, 0, 255),
            (position[0], position[1], size[0], size[1]),
            width=0,
        )

        # draw the white border
        pygame.draw.rect(
            self.game.screen,
            (255, 255, 255),
            (position[0], position[1], size[0], size[1]),
            width=2,
        )

    def draw_box_centered(self, position: tuple, size: tuple):
        if self.elapsed() < self.box_delay:
            # expand the box from it's center to it's full size

            size = (
                size[0] * self.elapsed() / self.box_delay,
                size[1] * self.elapsed() / self.box_delay,
            )

            # draw the blue background
            pygame.draw.rect(
                self.game.screen,
                (0, 0, 255),
                (
                    position[0] - size[0] / 2,
                    position[1] - size[1] / 2,
                    size[0],
                    size[1],
                ),
                width=0,
            )

            # draw the white border
            pygame.draw.rect(
                self.game.screen,
                (255, 255, 255),
                (
                    position[0] - size[0] / 2,
                    position[1] - size[1] / 2,
                    size[0],
                    size[1],
                ),
                width=2,
            )

            return

        # create a drop shadow for the box
        for i in range(1, self.shadow_depth + 1):
            self.draw_rect_alpha(
                self.game.screen,
                (0, 0, 0, self.shadow_intensity),
                (
                    position[0] - size[0] / 2 + i,
                    position[1] - size[1] / 2 + i,
                    size[0],
                    size[1],
                ),
            )

        # draw the blue background
        pygame.draw.rect(
            self.game.screen,
            (0, 0, 255),
            (position[0] - size[0] / 2, position[1] - size[1] / 2, size[0], size[1]),
            width=0,
        )

        # draw the white border
        pygame.draw.rect(
            self.game.screen,
            (255, 255, 255),
            (position[0] - size[0] / 2, position[1] - size[1] / 2, size[0], size[1]),
            width=2,
        )

    def draw_rect_alpha(self, surface, color, rect):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)

    def make_transparent_surface(self, size):
        return pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

    def make_text(
        self,
        text,
        color,
        fontSize,
        font=None,
        stroke=False,
        strokeColor=(0, 0, 0),
        strokeThickness=1,
    ):
        if font is None:
            font = "assets/fonts/" + settings.FONT

        # if we aren't stroking return the text directly
        if not stroke:
            return pygame.font.Font(font, fontSize).render(text, 1, color)

        # if we are stroking, render the text with the stroke
        # first render the text without the stroke

        # create a version of the text in the stroke color and blit it to the surface
        surf_text = pygame.font.Font(font, fontSize).render(text, 1, color)
        surf_text_stroke = pygame.font.Font(font, fontSize).render(text, 1, strokeColor)

        # create a transparent surface to draw the text and stroke on
        size = (
            surf_text.get_width() + strokeThickness * 3,
            surf_text.get_height() + strokeThickness * 3,
        )
        surface = self.make_transparent_surface(size)

        # blit the stroke text to the surface
        for i in range(strokeThickness * 2 + 1):
            for j in range(strokeThickness * 2 + 1):
                surface.blit(surf_text_stroke, (i, j))

        # blit the text on top of the stroke
        surface.blit(surf_text, (strokeThickness, strokeThickness))

        # return the surface
        return surface

    def blit_centered(self, source, target, position=(0.5, 0.5)):
        """
        This function places a given surface at a specified position on the target surface.

        Parameters:
        source (pygame.Surface): The source surface to be placed. This is a pygame Surface object, which can be
        created using pygame.font.Font.render() method.

        target (pygame.Surface): The target surface on which the surface is to be placed. This could be
        the game screen or any other surface.

        position (tuple): A tuple of two values between 0 and 1, representing the relative position
        on the target surface where the surface should be placed. The values correspond to the horizontal
        and vertical position respectively. For example, a position of (0.5, 0.5) will place the text dead
        center on the target surface.


        """
        source_position = source.get_rect()
        source_position.centerx = target.get_rect().centerx * position[0] * 2
        source_position.centery = target.get_rect().centery * position[1] * 2
        target.blit(source, source_position)

    def play_sound(self, sound):
        # verify the sound is loaded
        if sound not in self.game.sfx:
            print("Sound not found: " + sound)
            return

        print("play_sound: " + sound)

        # set the volume of the sound based on the settings
        self.game.sfx[sound].set_volume(self.game.volume_effects / 100)

        pygame.mixer.Sound.play(self.game.sfx[sound])

    # from the pygame tutorial:
    # https://www.pygame.org/docs/tut/tom_games3.html
    def load_png(self, name):
        """Load image and return image object"""
        fullname = os.path.join("assets/images", name)
        try:
            image = pygame.image.load(fullname)
            if image.get_alpha() is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
        except FileNotFoundError:
            print(f"Cannot load image: {fullname}")
            raise SystemExit
        return image, image.get_rect()
