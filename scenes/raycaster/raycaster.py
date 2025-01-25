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
        self.log(
            f"Camera Angle:    {self.camera.angle} ({math.degrees(self.camera.angle)})"
        )

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
        turn_factor = 0.02
        speed_factor = 0.15

        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if self.game.pressed[pygame.K_LEFT]:
            self.camera.angle -= turn_factor

        if self.game.pressed[pygame.K_RIGHT]:
            self.camera.angle += turn_factor

        if self.game.pressed[pygame.K_UP]:
            self.camera.pos = (
                self.camera.pos[0] + math.cos(self.camera.angle) * speed_factor,
                self.camera.pos[1] + math.sin(self.camera.angle) * speed_factor,
            )

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_walls()
        self.draw_map()

    def draw_walls(self):
        render_width = self.game.WIDTH
        fov = 90
        left_start = fov // 2 - fov
        right_end = fov // 2

        for i in range(render_width):
            angle = map_range(i, 0, render_width, left_start, right_end)

            # convert to radians
            angle = math.radians(angle) + self.camera.angle
            distance = self.level_map.wall_distance(self.camera.pos, angle)

            if distance:
                distance *= 7
                color = max(20, 255 - distance)
                wall_color = (color, color, color)

                distance *= math.cos(self.camera.angle - angle)
                wall_height = map_range(distance, 0, render_width, render_width, 0)

                pygame.draw.line(
                    self.screen,
                    wall_color,
                    (i, wall_height / 2),
                    (i, self.game.HEIGHT - wall_height / 2),
                )

    def draw_map(self):
        # draw the map for reference
        self.screen.blit(self.level_map.map, (0, 0))

        # draw a 3 px red line to represent the camera facing direction
        x, y = self.camera.pos
        dx = math.cos(self.camera.angle) * 3
        dy = math.sin(self.camera.angle) * 3
        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x + dx, y + dy), 1)


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


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
