import pygame
from scene import Scene
from utils import *
import os
import math


class RayCaster(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_map = LevelMap(0)
        self.camera = Camera(self.level_map.camera_start())
        self.commands = {
            "camera": self.command_camera,
            "distance": self.command_distance,
        }

    def command_camera(self):
        self.log(f"Camera Position: {self.camera.pos}")
        self.log(f"Camera Angle:    {self.camera.angle}")

    def command_distance(self):
        distance = self.level_map.wall_distance(self.camera.pos, self.camera.angle)
        # if distance:
        #     self.log(f"Distance: {distance}")
        dist = self.level_map.wall_distance(self.camera.pos, self.camera.angle)
        if dist:
            self.log(f"Distance: {dist}")
        else:
            self.log("Distance: Infinity")

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
        # draw the map for reference
        self.screen.blit(self.level_map.map, (0, 0))


class Camera:
    def __init__(self, pos=(0, 0)):
        self.pos = pos
        self.angle = 0


class LevelMap:
    def __init__(self, level_number):
        map_path = f"raycaster/maps/{level_number}.png"

        # check if the map file exists
        if not os.path.exists("assets/" + map_path):
            raise FileNotFoundError(f"Map file {map_path} not found")

        self.map = load_tpng(map_path)

    def camera_start(self):
        # determine the x, y position of the camera by the red pixel (255, 0, 0)

        for y in range(self.map.get_height()):
            for x in range(self.map.get_width()):
                if self.map.get_at((x, y)) == (255, 0, 0):
                    return (x, y)

        return (0, 0)  # default to 0, 0 if no red pixel is found

    def wall_distance(self, pos=(0, 0), angle=0) -> float | bool:
        x, y = pos
        dx = math.cos(angle)
        dy = math.sin(angle)

        while 0 <= x < self.map.get_width() and 0 <= y < self.map.get_height():
            if self.map.get_at((int(x), int(y))) == (255, 255, 255):
                return math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
            x += dx
            y += dy

        return False  # return infinity if no white pixel is found
