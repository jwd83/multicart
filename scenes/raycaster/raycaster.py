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
        self.draw_map()

    def draw_walls(self):
        render_width = self.game.WIDTH
        fov = 60
        half_fov = fov // 2
        fov_rad = math.radians(fov)
        fov_rad_half = math.radians(half_fov)

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

            intersections = []
            distances = []

            while True:
                ray_x += ray_dx
                ray_y += ray_dy

                if ray_x < 0 or ray_x >= self.level_map.map.get_width():
                    break

                if ray_y < 0 or ray_y >= self.level_map.map.get_height():
                    break

                tiles = []
                edges = set()

                for x in range(-1, 2):
                    for y in range(-1, 2):
                        tile_x = int(ray_x + x)
                        tile_y = int(ray_y + y)

                        tile_pos = (tile_x, tile_y)

                        if self.level_map.map.get_at(tile_pos) == wall_color:
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
                    intersection = self.level_map.line_intersection(
                        ray_x,
                        ray_y,
                        self.camera.pos[0],
                        self.camera.pos[1],
                        *edge,
                    )
                    if intersection:
                        distance = math.sqrt(
                            (self.camera.pos[0] - intersection[0]) ** 2
                            + (self.camera.pos[1] - intersection[1]) ** 2
                        )
                        intersections.append(intersection)
                        distances.append(distance)

                if len(distances) > 0:
                    break

            if len(distances) > 0:
                min_distance = min(distances)
                wall_height = (1 / min_distance) * self.game.HEIGHT
                top = (self.game.HEIGHT // 2) - (wall_height // 2)
                bottom = (self.game.HEIGHT // 2) + (wall_height // 2)
                pygame.draw.line(self.screen, (255, 0, 0), (i, top), (i, bottom), 1)

    def draw_map(self):
        # draw the map for reference
        self.screen.blit(self.level_map.map, (0, 0))

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

        self.map = load_tpng(map_path)

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
            if self.map.get_at((int(check[0]), int(check[1]))) == (255, 255, 255):
                return True
        return False

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
        hx = hy = vx = vy = -1
        distances = []

        # Check horizontal intersections
        if dy != 0:
            y_step = 1 if dy > 0 else -1
            y_intercept = math.ceil(y) if dy > 0 else math.floor(y)

            x_intercept = x + (y_intercept - y) / dy * dx
            while (
                0 <= x_intercept < self.map.get_width()
                and 0 <= y_intercept < self.map.get_height()
            ):
                if self.map.get_at((int(x_intercept), int(y_intercept))) == (
                    255,
                    255,
                    255,
                ):
                    hx = int(x_intercept)
                    hy = int(y_intercept)
                    hx1, hy1 = x, y
                    hx2, hy2 = x_intercept, y_intercept
                    break

                y_intercept += y_step
                x_intercept += y_step / dy * dx

        # Check vertical intersections
        if dx != 0:
            x_step = 1 if dx > 0 else -1
            x_intercept = math.ceil(x) if dx > 0 else math.floor(x)

            y_intercept = y + (x_intercept - x) / dx * dy
            while (
                0 <= x_intercept < self.map.get_width()
                and 0 <= y_intercept < self.map.get_height()
            ):
                if self.map.get_at((int(x_intercept), int(y_intercept))) == (
                    255,
                    255,
                    255,
                ):
                    vx = int(x_intercept)
                    vy = int(y_intercept)
                    vx1, vy1 = x, y
                    vx2, vy2 = x_intercept, y_intercept
                    break
                x_intercept += x_step
                y_intercept += x_step / dx * dy

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

        if hx == -1 and vx == -1:
            return float("inf")
        if hx >= 0:
            distances.append(self.box_line_intersection(hx, hy, hx1, hy1, hx2, hy2))
        if vx >= 0:
            distances.append(self.box_line_intersection(vx, vy, vx1, vy1, vx2, vy2))

        return min(distances)

    def box_line_intersection(self, box_x: int, box_y: int, x1, y1, x2, y2) -> float:
        min_distance = float("inf")
        edges = [
            (box_x, box_y, box_x + 1, box_y),
            (box_x, box_y, box_x, box_y + 1),
            (box_x + 1, box_y, box_x + 1, box_y + 1),
            (box_x, box_y + 1, box_x + 1, box_y + 1),
        ]
        for edge in edges:
            intersection = self.line_intersection(x1, y1, x2, y2, *edge)
            if intersection:
                distance = math.sqrt(
                    (x1 - intersection[0]) ** 2 + (y1 - intersection[1]) ** 2
                )
                min_distance = min(min_distance, distance)

        return min_distance

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
