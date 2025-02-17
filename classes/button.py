import pygame
import settings


class Button:
    def __init__(
        self,
        scene,
        screen,
        pos: tuple[int, int],
        size: tuple[int, int],
        content: str | pygame.surface.Surface,
        # properties for text buttons
        font=None,
        fontSize=30,
        color=(255, 255, 255),
        bg_color=(100, 100, 100),
    ):
        self.scene = scene
        self.screen = screen

        # If our content is a string, render the text onto a surface with any given settings
        if type(content) == str:
            pass
            # make a transparent surface for the button
            self.image = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

            # fill the image with gray
            self.image.fill(bg_color)

            # outline the image with a darker gray
            pygame.draw.rect(self.image, (50, 50, 50), (0, 0, size[0], size[1]), 2)

            # render the text onto the image

            text_image = self.scene.make_text(content, color, fontSize, font)

            # blit the text onto the center of the button
            self.image.blit(
                text_image,
                (
                    size[0] // 2 - text_image.get_width() // 2,
                    size[1] // 2 - text_image.get_height() // 2,
                ),
            )
        # otherwise it should be a surface, so we can just assign it to our image
        else:
            self.image = content

        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.clicked = False
        self.last_pressed = False
        self.activating = False

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
        if action:
            self.scene.play_sound("jsfxr-drop1")
        return action
