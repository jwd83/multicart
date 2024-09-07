import pygame
import settings


class Button:
    def __init__(
        self,
        screen,
        pos: tuple[int, int],
        size: tuple[int, int],
        content: str | pygame.surface.Surface,
        # properties for text buttons
        font=None,
        fontSize=32,
        color=(255, 255, 255),
    ):

        self.screen = screen

        # If our content is a string, render the text onto a surface with any given settings
        if type(content) == str:
            self.image = pygame.transform.scale(
                self.make_text(content, color, fontSize, font), size
            )
        # otherwise it should be a surface, so we can just assign it to our image
        else:
            self.image = content

        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.clicked = False
        self.last_pressed = False
        self.activating = False

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

    def draw(self):
        action = False

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        in_button = self.rect.collidepoint(mouse_pos)

        # detect our mouse button down and up frame
        mouse_down = False
        mouse_up = False
        if mouse_pressed != self.last_pressed:
            mouse_down = mouse_pressed
            mouse_up = not mouse_pressed
        self.last_pressed = mouse_pressed

        if not in_button:
            # if the mouse leaves the button deactivate it
            self.activating = False
        else:

            # begin activating on a mouse button down inside the button
            if mouse_down:
                self.activating = True

            # confirm activation on a mouse button up inside the button
            if mouse_up and self.activating:
                action = True
                self.activating = False

        # offset button for float/pending activation
        offset = self.rect.copy()
        if self.activating:
            # draw our button indented while activating
            offset.x += 2
            offset.y += 2
        else:
            # draw the mouse hover outdent while hovered
            if in_button:
                offset.x -= 1
                offset.y -= 1

        self.screen.blit(self.image, offset)
        return action
