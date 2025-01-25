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
        dist = self.level_map.wall_distance(self.camera.pos, self.camera.angle)
        if dist:
            self.log(f"Distance: {dist}")
        else:
            self.log("Distance: Infinity")

    def update(self):
        turn_factor = 0.03
        speed_factor = 0.05

        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if self.game.pressed[pygame.K_LEFT]:
            self.camera.angle -= turn_factor

        if self.game.pressed[pygame.K_RIGHT]:
            self.camera.angle += turn_factor

        if self.game.pressed[pygame.K_UP]:
            new_pos = (
                self.camera.pos[0] + math.cos(self.camera.angle) * speed_factor,
                self.camera.pos[1] + math.sin(self.camera.angle) * speed_factor,
            )
            if not self.level_map.wall_collision(new_pos):
                self.camera.pos = new_pos

        if self.game.pressed[pygame.K_DOWN]:
            new_pos = (
                self.camera.pos[0] - math.cos(self.camera.angle) * speed_factor,
                self.camera.pos[1] - math.sin(self.camera.angle) * speed_factor,
            )
            if not self.level_map.wall_collision(new_pos):
                self.camera.pos = new_pos

    def draw(self):
        # self.screen.fill((0, 0, 0))
        # draw the top half of the screen sky blue
        self.screen.fill((135, 206, 235))
        # draw the bottom half of the screen ground green
        pygame.draw.rect(
            self.screen,
            (0, 255, 0),
            (0, self.game.HEIGHT // 2, self.game.WIDTH, self.game.HEIGHT // 2),
        )
        self.draw_walls()
        self.draw_map()

    def draw_walls(self):
        render_width = self.game.WIDTH
        fov = 60
        left_start = fov // 2 - fov
        right_end = fov // 2
        max_height = self.game.HEIGHT
        min_height = 1

        for i in range(render_width):

            # convert to radians
            angle = (
                math.radians(map_range(i, 0, render_width, left_start, right_end))
                + self.camera.angle
            )
            distance = self.level_map.wall_distance(self.camera.pos, angle)

            if distance != float("inf"):

                color = max(20, 255 - distance * 5)
                wall_color = (color, 0, 0)
                wall_height = (1 / (distance)) * max_height
                top = (self.game.HEIGHT // 2) - (wall_height // 2)
                bottom = (self.game.HEIGHT // 2) + (wall_height // 2)
                pygame.draw.line(self.screen, wall_color, (i, top), (i, bottom), 1)

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

    def wall_collision(self, pos=(0, 0)) -> bool:
        x, y = pos
        return self.map.get_at((int(x), int(y))) == (255, 255, 255)

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
            map_x = math.floor(x)
            map_y = math.floor(y)

            if self.map.get_at((map_x, map_y)) == (255, 255, 255):
                # now that we know the intersection is in this square, we can calculate
                # where the intersection occurs along the edge of the square and return
                # the distance to that intersection
                # return math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
                edges = [
                    (map_x, map_y, map_x + 1, map_y),
                    (map_x, map_y, map_x, map_y + 1),
                    (map_x + 1, map_y, map_x + 1, map_y + 1),
                    (map_x, map_y + 1, map_x + 1, map_y + 1),
                ]

                x1 = x
                y1 = y

                x2 = x - dx
                y2 = y - dy
                for edge in edges:
                    intersection = self.line_intersection(x1, y1, x2, y2, *edge)
                    if intersection:
                        x, y = intersection
                        return math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)

            x += dx
            y += dy

        # No intersection found, return infinity
        return float("inf")

    def line_intersection(self, ax1, ay1, ax2, ay2, bx1, by1, bx2, by2) -> float:
        # calculate the intersection point of two lines
        # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        # (x1, y1) (x2, y2) is the first line
        # (x3, y3) (x4, y4) is the second line

        x1, y1, x2, y2 = ax1, ay1, ax2, ay2
        x3, y3, x4, y4 = bx1, by1, bx2, by2

        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if d == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d

        u = (-((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))) / d

        if 0 <= t <= 1 and 0 <= u <= 1:
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        else:
            return None
