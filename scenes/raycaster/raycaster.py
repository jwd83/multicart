from scene import Scene
from utils import *
import math
import numpy as np
import os
import pygame
from numba import njit, jit
import os
import pygame

BASE_IMAGE_PATH = "assets/raycaster/"
PI_2 = math.pi * 2


class RayCaster(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.fov_degrees = 60
        self.fov_degrees_half = self.fov_degrees // 2
        self.fov_rad = math.radians(self.fov_degrees)
        self.fov_rad_half = math.radians(self.fov_degrees_half)

        self.level = LevelMap(1)
        self.camera = Camera(self.level.pos_camera_start)
        self.commands = {
            "camera": self.command_camera,
        }
        self.render_scale = 1
        self.render_height = self.game.HEIGHT // self.render_scale
        self.render_width = self.game.WIDTH // self.render_scale
        self.distances = np.zeros(self.render_width)
        self.rads = np.zeros(self.render_width)
        self.wall_points = np.zeros((self.render_width, 2))
        self.display = self.make_surface((self.render_width, self.render_height))
        self.assets = {
            "tree": load_image("textures/tree.png"),
            "bricks": load_image("textures/bricks.png"),
        }

    def command_camera(self):
        self.log(f"Camera Position: {self.camera.pos}")
        self.log(
            f"Camera Angle:    {self.camera.angle} ({math.degrees(self.camera.angle)})"
        )

    def update(self):
        turn_factor = 0.03
        speed_factor = 0.05

        if self.game.pressed[pygame.K_LSHIFT]:
            speed_factor = 0.1

        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        # turn left/right
        if self.game.pressed[pygame.K_LEFT]:
            self.camera.angle -= turn_factor

        if self.game.pressed[pygame.K_RIGHT]:
            self.camera.angle += turn_factor

        # cap the angle to 2pi
        if self.camera.angle > PI_2:
            self.camera.angle -= PI_2

        if self.camera.angle < 0:
            self.camera.angle += PI_2

        if self.game.pressed[pygame.K_UP]:
            new_pos = (
                self.camera.pos[0] + math.cos(self.camera.angle) * speed_factor,
                self.camera.pos[1] + math.sin(self.camera.angle) * speed_factor,
            )
            if not self.level.wall_collision(new_pos):
                self.camera.pos = new_pos

        if self.game.pressed[pygame.K_DOWN]:
            new_pos = (
                self.camera.pos[0] - math.cos(self.camera.angle) * speed_factor,
                self.camera.pos[1] - math.sin(self.camera.angle) * speed_factor,
            )
            if not self.level.wall_collision(new_pos):
                self.camera.pos = new_pos

    def draw(self):
        # self.display.fill((0, 0, 0))
        # draw the top half of the screen sky blue
        self.display.fill((135, 206, 235))
        # draw the bottom half of the screen ground green
        pygame.draw.rect(
            self.display,
            (160, 160, 165),
            (0, self.render_height // 2, self.render_width, self.render_height // 2),
        )

        self.draw_walls()
        # self.draw_objects()
        self.draw_map()

        # scale the display to the game window size
        if self.render_scale > 1:
            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
        else:
            self.screen.blit(self.display, (0, 0))

    def draw_objects(self):
        # make a list of objects in our fov
        render_objects = []
        for obj in self.level.level_objects:
            angle = math.atan2(
                obj.pos[1] - self.camera.pos[1], obj.pos[0] - self.camera.pos[0]
            )
            angle_diff = abs(self.camera.angle - angle)
            # self.log(f"Angle: {angle}, Angle Diff: {angle_diff}")
            if (
                abs(angle_diff) < self.fov_rad_half
                or abs(angle_diff) > PI_2 - self.fov_rad_half
            ):
                distance = line_distance(*self.camera.pos, *obj.pos)
                render_objects.append((distance, angle, obj))

        # sort the objects by distance  so we can render them in the correct order
        render_objects.sort(key=lambda x: x[0])

        x1 = self.camera.pos[0]
        y1 = self.camera.pos[1]

        for i in range(self.render_width):
            x2 = self.wall_points[i, 0]
            y2 = self.wall_points[i, 1]

            for obj in render_objects:
                # check if the object is in front of the wall for this column
                edges = self.tile_edges(int(obj[2].pos[0]), int(obj[2].pos[1]))
                dist = self.intersect_edges(edges, x1, y1, x2, y2, i)
                if dist < self.distances[i]:
                    pass
                    # self.draw_slice(
                    #     i,
                    #     self.distances[i],
                    #     (max(20, 0, int(255 - self.distances[i] * 7)), 0),
                    # )

    def draw_walls(self):

        cam_angle = self.camera.angle

        x = self.camera.pos[0]
        y = self.camera.pos[1]

        for i in range(self.render_width):
            render_x_pct = i / (self.render_width - 1)
            render_rad = cam_angle - self.fov_rad_half + self.fov_rad * render_x_pct
            self.rads[i] = render_rad
            self.distances[i] = self.wall_distance(x, y, render_rad, i)
            self.draw_slice(i)

    def draw_slice(self, x):
        distance = self.distances[x]

        bricks = self.assets["bricks"]

        # determine the position of the slice we need to draw
        wp_x = self.wall_points[x, 0]
        wp_y = self.wall_points[x, 1]
        texture_x = abs(wp_x - int(wp_x)) + abs(wp_y - int(wp_y))
        texture_x = self.constrain(texture_x, 0, 1)
        texture_x = int(texture_x * bricks.get_width() - 1)

        wall_height = min((1 / distance) * self.render_height, self.render_height)
        wall_height = self.constrain(wall_height, 5, self.render_height)
        top = (self.render_height // 2) - (wall_height // 2)

        self.display.blit(
            pygame.transform.scale(
                bricks.subsurface(texture_x, 0, 1, bricks.get_height()),
                (1, int(wall_height)),
            ),
            (x, top),
        )

    def tile_edges(self, x, y):
        edges = []
        edges.append((x, y, x + 1, y))  # top
        edges.append((x + 1, y, x + 1, y + 1))  # right
        edges.append((x, y + 1, x + 1, y + 1))  # bottom
        edges.append((x, y, x, y + 1))  # left
        return edges

    def wall_distance(self, x, y, radians, i) -> float:
        distance = 9999
        x1 = x2 = x
        y1 = y2 = y
        dx = math.cos(radians)
        dy = math.sin(radians)

        edges_function = None

        if dx >= 0 and dy <= 0:
            edges_function = self.edges_ne
        elif dx >= 0 and dy > 0:
            edges_function = self.edges_se
        elif dx < 0 and dy <= 0:
            edges_function = self.edges_nw
        else:
            edges_function = self.edges_sw

        while True:
            y2 += dy
            x2 += dx

            if x2 < 0 or x2 >= self.level.map_width:
                break

            if y2 < 0 or y2 >= self.level.map_height:
                break

            edges = edges_function(x1, y1, x2, y2)
            dist = self.intersect_edges(edges, x1, y1, x2, y2, i)
            if dist:
                # self.log(dist)
                distance = dist
                break

        return distance

    def intersect_edges(self, edges, x1, y1, x2, y2, i):
        min_dist = None

        if not edges:
            return min_dist
        for edge in edges:
            new_dist = False
            intersection = line_intersection(x1, y1, x2, y2, *edge)
            if intersection:
                dist = line_distance(x1, y1, intersection[0], intersection[1])
                if dist and min_dist is None:
                    new_dist = True
                elif dist < min_dist:
                    new_dist = True

                if new_dist:
                    min_dist = dist
                    self.wall_points[i, 0] = intersection[0]
                    self.wall_points[i, 1] = intersection[1]

        return min_dist

    def edges_ne(self, x1, y1, x2, y2):
        # working!
        edges = []

        x = int(x2)
        y = int(y2)

        a = (x, y + 1)
        b = (a[0] + 1, a[1])
        c = (a[0], a[1] - 1)
        d = (a[0] - 1, a[1])
        e = (a[0], a[1] + 1)

        tile_ne = self.level.map[a[0], a[1] - 1] > 0
        tile_nw = self.level.map[a[0] - 1, a[1] - 1] > 0
        tile_se = self.level.map[a[0], a[1]] > 0
        tile_sw = self.level.map[a[0] - 1, a[1]] > 0

        # calculate horizontal edge
        if tile_ne and tile_nw:
            edges.append((*b, *d))
        else:
            if tile_ne:
                edges.append((*a, *b))
            if tile_nw:
                edges.append((*a, *d))
        # calculate vertical edge
        if tile_ne and tile_se:
            edges.append((*c, *e))
        else:
            if tile_ne:
                edges.append((*a, *c))
            if tile_se:
                edges.append((*a, *e))

        return edges

    def edges_nw(self, x1, y1, x2, y2) -> float:

        edges = []

        x = int(x2)
        y = int(y2)

        a = (x + 1, y + 1)
        b = (a[0] + 1, a[1])
        c = (a[0], a[1] - 1)
        d = (a[0] - 1, a[1])
        e = (a[0], a[1] + 1)

        tile_ne = self.level.map[a[0], a[1] - 1] > 0
        tile_nw = self.level.map[a[0] - 1, a[1] - 1] > 0
        tile_se = self.level.map[a[0], a[1]] > 0
        tile_sw = self.level.map[a[0] - 1, a[1]] > 0

        # calculate horizontal edge
        if tile_ne and tile_nw:
            edges.append((*b, *d))
        else:
            if tile_ne:
                edges.append((*a, *b))
            if tile_nw:
                edges.append((*a, *d))
        # calculate vertical edge
        if tile_nw and tile_sw:
            edges.append((*c, *e))
        else:
            if tile_nw:
                edges.append((*a, *c))
            if tile_sw:
                edges.append((*a, *e))

        return edges

    def edges_sw(self, x1, y1, x2, y2) -> float:

        edges = []

        x = int(x2)
        y = int(y2)

        a = (x + 1, y)
        b = (a[0] + 1, a[1])
        c = (a[0], a[1] - 1)
        d = (a[0] - 1, a[1])
        e = (a[0], a[1] + 1)

        tile_ne = self.level.map[a[0], a[1] - 1] > 0
        tile_nw = self.level.map[a[0] - 1, a[1] - 1] > 0
        tile_se = self.level.map[a[0], a[1]] > 0
        tile_sw = self.level.map[a[0] - 1, a[1]] > 0

        # calculate horizontal edge
        if tile_se and tile_sw:
            edges.append((*b, *d))
        else:
            if tile_se:
                edges.append((*a, *b))
            if tile_sw:
                edges.append((*a, *d))
        # calculate vertical edge
        if tile_nw and tile_sw:
            edges.append((*c, *e))
        else:
            if tile_nw:
                edges.append((*a, *c))
            if tile_sw:
                edges.append((*a, *e))

        return edges

    def edges_se(self, x1, y1, x2, y2) -> float:

        edges = []

        x = int(x2)
        y = int(y2)

        a = (x, y)
        b = (a[0] + 1, a[1])
        c = (a[0], a[1] - 1)
        d = (a[0] - 1, a[1])
        e = (a[0], a[1] + 1)

        tile_ne = self.level.map[a[0], a[1] - 1] > 0
        tile_nw = self.level.map[a[0] - 1, a[1] - 1] > 0
        tile_se = self.level.map[a[0], a[1]] > 0
        tile_sw = self.level.map[a[0] - 1, a[1]] > 0

        # calculate horizontal edge
        if tile_se and tile_sw:
            edges.append((*b, *d))
        else:
            if tile_se:
                edges.append((*a, *b))
            if tile_sw:
                edges.append((*a, *d))
        # calculate vertical edge
        if tile_ne and tile_se:
            edges.append((*c, *e))
        else:
            if tile_ne:
                edges.append((*a, *c))
            if tile_se:
                edges.append((*a, *e))

        return edges

    def draw_map(self):
        # draw the map for reference
        self.display.blit(self.level.map_data, (0, 0))

        # draw a 3 px red line to represent the camera facing direction
        x, y = self.camera.pos
        dx = math.cos(self.camera.angle) * 3
        dy = math.sin(self.camera.angle) * 3

        pygame.draw.rect(self.display, (0, 0, 255), (x - 1, y - 1, 3, 3))
        pygame.draw.line(self.display, (255, 0, 0), (x, y), (x + dx, y + dy), 1)


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
        self.level_objects = []

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

                if self.map_data.get_at((x, y)) == (0, 255, 0):
                    self.level_objects.append(LevelObject((x, y), "tree"))

    def wall_collision(self, pos=(0, 0)) -> bool:

        x = int(pos[0])
        y = int(pos[1])
        return self.map[x, y] == 1


class LevelObject:
    def __init__(self, pos=(0, 0), type="tree"):
        self.pos = pos
        self.type = type


def line_intersection(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
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


def line_distance(x1, y1, x2, y2) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# load a single image
def load_image(path):
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


# load all images in a directory
def load_images(path):
    images = []

    for img_name in sorted(
        os.listdir(BASE_IMAGE_PATH + path)
    ):  # sorted is used for OS interoperability
        images.append(load_image(path + "/" + img_name))

    return images
