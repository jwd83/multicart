# this file is just for reference, it is not used in the game

import pygame
from scene import Scene
from utils import *

class Console(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.background = self.make_transparent_surface(self.screen.get_size())
        self.background.fill((0, 0, 0, 200))
        self.history = []
        self.command = ""
        self.active = False

    def update(self):

        self.command += self.game.unicode

        for k in self.game.just_pressed:
        
            # execute the command in the console
            if k == pygame.K_RETURN:
                self.history.append("<<" + self.command)
                if self.command == "exit" or self.command == "quit":
                    self.game.quit = True
                else:
                    # try to execute the command
                    try:
                        exec(self.command)
                    except Exception as e:
                        self.history.append(f"Error: {e}")
                        
                self.command = ""
                continue
            
            # delete the last character in the command
            if k == pygame.K_BACKSPACE:
                self.command = self.command[:-1]
                continue
        
        # # clear the command
        # char = self.key_to_char(k)
        # print(f"Key: {k} Char: {char}")
        # self.command += char

    def key_to_char(self, key):
        # space bar
        if key == pygame.K_SPACE:
            return " "
        
        # letters
        if key >= pygame.K_a and key <= pygame.K_z:
            if self.game.pressed[pygame.K_LSHIFT] or self.game.pressed[pygame.K_RSHIFT]:
                return chr(key).upper()
            else:
                return chr(key)
        
        # numbers
        if key >= pygame.K_0 and key <= pygame.K_9:
            if self.game.pressed[pygame.K_LSHIFT] or self.game.pressed[pygame.K_RSHIFT]:
                return ")!@#$%^&*("[key - pygame.K_0]
            else:
                return chr(key)

        # special characters
        if key < 254:
            if self.game.pressed[pygame.K_LSHIFT] or self.game.pressed[pygame.K_RSHIFT]:
                return chr(key-32)
            else:
                return chr(key)

        return ""

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.standard_font_size = 20
        self.standard_color = (255, 255, 255)
        self.screen.blit(self.standard_text("PyGame Console"), (10, 10))
        self.screen.blit(self.standard_text(self.command), (10, 20))

        # draw the last 5 history elements
        for i, h in enumerate(self.history[-5:]):
            self.screen.blit(self.standard_text(h), (10, 30 + 10 * i))
