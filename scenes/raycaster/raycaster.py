from scene import Scene
from utils import *
import math
import numpy as np
import os
import pygame


class RayCaster(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_map = LevelMap(0)
        self.camera = Camera(self.level_map.pos_camera_start)
        self.commands = {
            "camera": self.command_camera,
        }

    def command_camera(self):
        self.log(f"Camera Position: {self.camera.pos}")
        self.log(
            f"Camera Angle:    {self.camera.angle} ({math.degrees(self.camera.angle)})"
        )

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
        self.draw_walls_plus()
        self.draw_map()

    def draw_walls_plus(self):

        return
        render_width = self.game.WIDTH
        render_height = self.game.HEIGHT
        fov = 60
        half_fov = fov // 2
        fov_rad = math.radians(fov)
        fov_rad_half = math.radians(half_fov)
        map_width = self.level_map.map_data.get_width()
        map_height = self.level_map.map_data.get_height()

    def draw_walls(self):
        render_width = self.game.WIDTH
        render_height = self.game.HEIGHT
        fov = 60
        half_fov = fov // 2
        fov_rad = math.radians(fov)
        fov_rad_half = math.radians(half_fov)
        map_width = self.level_map.map_data.get_width()
        map_height = self.level_map.map_data.get_height()

        wall_color = (255, 255, 255)

        for i in range(render_width):

            render_width_percent = i / (render_width - 1)
            render_rad = (
                self.camera.angle - fov_rad_half + fov_rad * render_width_percent
            )

            ray_dx = math.cos(render_rad)
            ray_dy = math.sin(render_rad)
            ray_x = self.camera.pos[0]
            ray_y = self.camera.pos[1]

            distances = []

            while True:
                ray_x += ray_dx
                ray_y += ray_dy

                if ray_x < 0 or ray_x >= map_width:
                    break

                if ray_y < 0 or ray_y >= map_height:
                    break

                tiles = []
                edges = set()

                for x in range(-1, 2):
                    for y in range(-1, 2):
                        tile_x = int(ray_x + x)
                        tile_y = int(ray_y + y)

                        tile_pos = (tile_x, tile_y)

                        if self.level_map.map_data.get_at(tile_pos) == wall_color:
                            tiles.append(tile_pos)

                if len(tiles) > 0:
                    for tile in tiles:
                        # top
                        # left
                        # right
                        # bottom

                        edges.add((tile[0], tile[1], tile[0] + 1, tile[1]))
                        edges.add((tile[0], tile[1], tile[0], tile[1] + 1))
                        edges.add((tile[0] + 1, tile[1], tile[0] + 1, tile[1] + 1))
                        edges.add((tile[0], tile[1] + 1, tile[0] + 1, tile[1] + 1))

                for edge in edges:
                    intersection = line_intersection(
                        ray_x,
                        ray_y,
                        self.camera.pos[0],
                        self.camera.pos[1],
                        *edge,
                    )
                    if intersection:
                        distance = line_distance(
                            self.camera.pos[0],
                            self.camera.pos[1],
                            intersection[0],
                            intersection[1],
                        )
                        distances.append(distance)

                if len(distances) > 0:
                    break

            if len(distances) > 0:
                min_distance = min(distances)
                wall_height = (1 / min_distance) * render_height
                top = (render_height // 2) - (wall_height // 2)
                bottom = (render_height // 2) + (wall_height // 2)
                red_color = max(20, int(255 - min_distance * 8))
                pygame.draw.line(
                    self.screen, (red_color, 0, 0), (i, top), (i, bottom), 1
                )

    def draw_map(self):
        # draw the map for reference
        self.screen.blit(self.level_map.map_data, (0, 0))

        # draw a 3 px red line to represent the camera facing direction
        x, y = self.camera.pos
        dx = math.cos(self.camera.angle) * 3
        dy = math.sin(self.camera.angle) * 3
        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x + dx, y + dy), 1)


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

        self.pos_camera_start = (0, 0)

        self.map_data = load_tpng(map_path)

        self.map_height = self.map_data.get_height()
        self.map_width = self.map_data.get_width()

        self.map = np.zeros((self.map_width, self.map_height))

        self.parse_map()

    def parse_map(self):
        self.map = np.zeros((self.map_width, self.map_height))
        for x in range(self.map_width):
            for y in range(self.map_height):
                if self.map_data.get_at((x, y)) == (255, 255, 255):
                    self.map[x, y] = 1

                if self.map_data.get_at((x, y)) == (255, 0, 0):
                    self.pos_camera_start = (x, y)

    def wall_collision(self, pos=(0, 0)) -> bool:
        x, y = pos
        checks = [
            (x, y),
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x - 1, y),
            (x + 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x + 1, y + 1),
        ]
        for check in checks:
            if self.map_data.get_at((int(check[0]), int(check[1]))) == (255, 255, 255):
                return True
        return False


# @njit
def line_intersection(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2) -> float:
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


# @njit
def line_distance(x1, y1, x2, y2) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
