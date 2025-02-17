import time
import math
import pygame
import settings
import os


class FastText(pygame.sprite.Sprite):
    def __init__(self, scene: "Scene", text: str, pos: tuple, anchor: str = "topleft"):
        super().__init__()
        # this must be set before text for the setattr trigger to work
        self.__last_rendered_text: str | None = None
        # this must be set before pos for the setattr trigger to work
        self.rect: pygame.Rect | None = None
        self.pos: tuple = pos
        self.scene: Scene = scene
        self.image: pygame.Surface = None
        self.anchor: str = anchor

        # this will trigger the __render method so assign it last
        self.text: str = text

    def __setattr__(self, name, value):
        # Call the original __setattr__
        super().__setattr__(name, value)

        # If the attribute being changed is 'text', call __render
        if name == "text":
            self.__render()

        # If the attribute being changed is 'pos' update the rect
        if name == "pos" and self.rect is not None:
            setattr(self.rect, self.anchor, value)

    def __render(self):
        if self.text != self.__last_rendered_text:

            self.image = self.scene.standard_text(self.text)
            self.rect = self.image.get_rect()
            setattr(self.rect, self.anchor, self.pos)
            self.__last_rendered_text = self.text

    def draw(self):
        self.scene.screen.blit(self.image, self.pos)


class Scene:

    def __init__(self, game):
        # prevent circular import by importing game here for type hinting
        import game as g

        # store the reference to the game object and add the type annotation
        # for type hinting in our editor. This is not necessary for the code to run.
        self.game: g.Game = game
        self.mouse_lock = False
        self.mouse_hide = False
        self.active = True
        self.screen: pygame.Surface = game.screen
        self.start = time.time()
        self.shadow_intensity = 100
        self.shadow_depth = 3
        self.box_delay = 0.25
        self.standard_stroke = True
        self.standard_stroke_color = (200, 80, 80)
        self.standard_stroke_thickness = 1
        self.standard_font_size = 40
        self.standard_color = (240, 240, 240)
        self.standard_font = None  # use the default font
        self.__all_text = pygame.sprite.Group()
        self.commands = {
            "test": self.default_command,
        }  # console command dictionary of callable functions
        self.mouse_cursor, _ = self.load_png("pointer-outlined-small.png")

    def draw_mouse(self):

        # draw the mouse
        self.screen.blit(self.mouse_cursor, pygame.mouse.get_pos())

    def default_command(self, argument: str | None = None) -> None:
        if argument is not None:
            self.log(f"Hello, {argument}.")
        else:
            self.log("Hello, friend!")

        self.log("This is the default test command, it may optionally be")
        self.log("passed an argument. If an argument is passed, it will")
        self.log("be echoed back to you in the Hello message.")

    def draw_text(self):
        self.__all_text.draw(self.screen)

    def Text(self, text: str, pos: tuple, anchor: str = "topleft") -> FastText:
        """Generates a FastText object and adds it to the scene's all_text group.

        Args:
            text (str): The text to generate
            pos (tuple): The position of the text
            anchor (str, optional): Where to anchor the text such as center or topleft. Defaults to "topleft".

        Returns:
            FastText: a FastText object that has been added to the all_text group. Update it's text attribute to change the text automatically.
        """
        t = FastText(self, text, pos, anchor)
        self.__all_text.add(t)
        return t

    def blitRotateCenter(
        self, image, topleft, angle, destination_surface: pygame.Surface
    ):

        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

        destination_surface.blit(rotated_image, new_rect)

    def standard_text(
        self,
        text: str,
        font_size: int | None = None,
    ) -> pygame.Surface:

        if font_size is None:
            font_size = self.standard_font_size

        return self.make_text(
            text,
            self.standard_color,
            font_size,
            font=self.standard_font,
            stroke=self.standard_stroke,
            strokeColor=self.standard_stroke_color,
            strokeThickness=self.standard_stroke_thickness,
        )

    def elapsed(self):
        return time.time() - self.start

    def constrain(self, n, n_min, n_max):
        return max(min(n_max, n), n_min)

    def update(self):
        """This method should be implemented by the child class to update the scene."""
        self.log("Scene's update method has not been implemented")

    def draw(self):
        """This method should be implemented by the child class to draw the scene."""
        # the values of sin range from -1 to 1
        r = math.sin(time.time() * 1.33 + 1.5) * 127 + 128
        g = math.sin(time.time()) * 127 + 128
        b = math.sin(time.time() * 0.25 - 0.6666) * 127 + 128
        self.screen.fill((r, g, b))
        self.log("Scene's draw method has not been implemented")

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

    def make_surface(self, size) -> pygame.Surface:
        """an alias for make_transparent_surface

        Returns:
            pygame.Surface: a transparent surface
        """
        return self.make_transparent_surface(size)

    def make_transparent_surface(self, size) -> pygame.Surface:
        return pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

    def new_layer(self):
        """Creates a new surface layer to draw on the size of the screen."""

        return self.make_transparent_surface(
            (settings.RESOLUTION[0], settings.RESOLUTION[1])
        )

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

        if font == "system-ui":
            font = None

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
            self.log("play_sound: Sound not found: " + sound)
            return

        # set the volume of the sound based on the settings
        self.game.sfx[sound].set_volume(self.game.volume_effects / 100)

        pygame.mixer.Sound.play(self.game.sfx[sound])

    def play_music(self, path_in_assets):  # play a sound in an endless loop
        # stop any music that is currently playing
        pygame.mixer.music.stop()

        # check if path_in_assets exists in ./assets/
        if not os.path.exists("assets/" + path_in_assets):
            self.log("play_music: Music not found: " + path_in_assets)
            return

        # load the music
        pygame.mixer.music.load("assets/" + path_in_assets)

        # set the volume of the music based on the settings
        pygame.mixer.music.set_volume(self.game.volume_music / 100)

        # play the music in an endless loop
        pygame.mixer.music.play(-1)

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
            self.log(f"Cannot load image: {fullname}")
            raise SystemExit
        return image, image.get_rect()

    def log(self, message: str):
        """Calls the game objects log method with the message to make it easier to log messages from scenes.

        Args:
            message (str): The message to be logged
        """
        self.game.log(message)

    def quit(self):
        """Scenes can override this method to gracefully exit. This was added so QuadBlox
        could gracefully exit it's client thread.
        """
        self.log(
            f"Scene's quit method has not been implemented: {self.__class__.__name__}"
        )
