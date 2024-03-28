# this file is just for reference, it is not used in the game

import pygame
from scene import Scene
from utils import *
import numpy as np

class JackWizardsMap(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.map_image = load_tpng("jackwizards/dall-e-map.png")

        print("Rendering map: ", self.game.jw.level)

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_TAB in self.game.just_pressed:
            self.game.scene_pop = True

    def draw(self):
        print("Drawing map:")
        print(self.game.jw.level)
        # self.screen.fill((0, 0, 0))

        # draw the map image at the center of the screen
        x = (self.screen.get_width() - self.map_image.get_width()) // 2
        y = (self.screen.get_height() - self.map_image.get_height()) // 2
        self.screen.blit(self.map_image, (x, y))

        # draw the player's map

        box_space = 12
        box_size = 10
        top_start = 84
        left_start = 220
        hall_size = box_space - box_size

        for x in range(16):
            for y in range(16):
                # print(self.game.jw.level)
                room_flags = self.game.jw.level[x, y]

                dx = left_start + (x * box_space)
                dy = top_start + (y * box_space)

                print(x, y, dx, dy, box_size, box_size, ": ", room_flags)

                self.screen.fill((180, 180, 180), (dx, dy, box_size, box_size))

                if room_flags > 0:

                    # check if player has the map in their inventory
                    if "map" in self.game.jw.player.inventory:
                        # draw a 4x4 px square for the room
                        self.screen.fill((0, 0, 0), (dx, dy, box_size, box_size))

                        self.screen.set_at((dx,dy), (80, 80, 80))

                        # draw the connecting hallways

                        # up hallway

                        if room_flags & 1:
                            self.screen.fill(
                                (0, 0, 0),
                                (dx + box_size // 2, dy - hall_size, hall_size, hall_size)
                            )

                        # down hallway
                        if room_flags & 4:
                            self.screen.fill(
                                (0, 0, 0),
                                (dx + box_size // 2, dy + hall_size, hall_size, hall_size)
                            )

                        # right hallway
                        if room_flags & 2:
                            self.screen.fill(
                                (0, 0, 0),
                                (dx + hall_size, dy + box_size // 2, hall_size, hall_size)
                            )

                        # left hallway
                        if room_flags & 8:
                            self.screen.fill(
                                (0, 0, 0),
                                (dx - hall_size, dy + box_size // 2, hall_size, hall_size)
                            )


                    # check if the compass is in the player's inventory
                    if "compass" in self.game.jw.player.inventory:
                        # draw a glowing red pixel for the boss room
                        if room_flags & 32:
                            self.screen.fill((255, 0, 0),(dx, dy, box_size, box_size))

        # draw a box for the player's current room
        dx = left_start + (self.game.jw.level_x * box_space)
        dy = top_start + (self.game.jw.level_y * box_space)
        self.screen.fill((255, 255, 255), (dx, dy, box_size, box_size))

