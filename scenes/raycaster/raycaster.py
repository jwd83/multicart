"""
todo:
* a crosshair in the center of the screen
* mouse movement
* player shoot, muzzle flare and sound. if monster hit remove from level monsters and put a toad death in level objects to store where the body was killed.
* maybe after walls and floors are drawn do a pool of blood pass on any dead monsters before rendering objects for some extra gore
* bring the animatedsprite and animation classes in to load the walk animation for the toad monster
* path finding for the toad monster class to locate the player
* draw objects needs to clip out of view portions of the object. determine left and right edges of the object to clip the sprite to

"""

from scene import Scene
from utils import *
import math
import numpy as np
import os
import pygame
from numba import njit, jit
import os
import pygame
from classes import *

BASE_IMAGE_PATH = "assets/raycaster/"
PI_2 = math.pi * 2


class RayCaster(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.fov_degrees = 60
        self.fov_degrees_half = self.fov_degrees // 2
        self.fov_rad = math.radians(self.fov_degrees)
        self.fov_rad_half = math.radians(self.fov_degrees_half)

        self.level = LevelMap(1, self)
        self.camera = Camera(self.level.pos_camera_start)
        self.commands = {
            "camera": self.command_camera,
            "monsters": self.command_monsters,
            "spawn": self.command_spawn,
        }
        self.move_start = 0
        self.render_scale = 1
        self.render_height = self.game.HEIGHT // self.render_scale
        self.render_width = self.game.WIDTH // self.render_scale
        self.distances = np.zeros(self.render_width)
        self.rads = np.zeros(self.render_width)
        self.wall_points = np.zeros((self.render_width, 2))
        self.wall_textures = np.zeros(self.render_width)
        self.display = self.make_surface((self.render_width, self.render_height))
        self.assets = {
            "bricks": load_image("textures/bricks-bg-tiles.png"),
            "chandelier": load_image("textures/chandelier.png"),
            "flag": load_image("textures/flag.png"),
            "pistol": load_image("textures/pistol.png"),
            "rifle": load_image("textures/rifle.png"),
            "staggered": load_image("textures/staggered.png"),
            "toad/walk": Animation(
                load_images_alpha("animations/toad/walk"), img_dur=10
            ),
            "toad/die": Animation(
                load_images_alpha("animations/toad/die"), img_dur=10, loop=False
            ),
            "tree": load_image("textures/tree.png"),
            "telepad": load_image("textures/telepad.png"),
            "tree-big": load_image("textures/tree-big.png"),
            "wood": load_image("textures/wood-bg-tiles.png"),
        }
        self.inventory = ["pistol", "rifle"]
        self.ammo = 99
        self.spawn_rate = 60
        self.weapon = "rifle"

    def command_monsters(self):
        self.log(f"Monsters: {len(self.level.monsters)}")
        for monster in self.level.monsters:
            self.log(f"Monster: {monster.pos}")

    def command_spawn(self):
        self.level.spawn_monsters(1)

    def convert_radians_to_slice(self, radians):

        # for i in range(self.render_width):
        #     render_x_pct = i / (self.render_width - 1)
        #     render_rad = cam_angle - self.fov_rad_half + self.fov_rad * render_x_pct
        #     self.rads[i] = render_rad
        #     self.distances[i] = self.wall_distance(x, y, render_rad, i)

        a = radians - self.camera.angle + self.fov_rad_half
        b = self.render_width - 1
        c = self.fov_rad
        i = int((a * b) / c)
        return i % self.render_width

    def command_camera(self):
        self.log(f"Camera Position: {self.camera.pos}")
        self.log(
            f"Camera Angle:    {self.camera.angle} ({math.degrees(self.camera.angle)})"
        )

    def update(self):
        self.update_player()
        self.spawn_monsters()
        self.move_monsters()
        self.animate_monsters()

    def spawn_monsters(self):
        if self.game.frame_count() % self.spawn_rate == 0:
            if random.choice([True, False, False, False]):
                self.play_sound("jsfxr-qb-lines-4")
                self.level.spawn_monsters(1)

    def move_monsters(self):
        monster_speed = 0.03

        for monster in self.level.monsters:
            # move the monster toward the player

            # if the monster is less than 0.5 units away from the player then dont move
            # them any closer
            distance_to_player = math.sqrt(
                (self.camera.pos[0] - monster.pos[0]) ** 2
                + (self.camera.pos[1] - monster.pos[1]) ** 2
            )
            if distance_to_player < 0.5:
                continue

            # get the angle to the player
            angle = math.atan2(
                self.camera.pos[1] - monster.pos[1], self.camera.pos[0] - monster.pos[0]
            )

            # move the monster toward the player
            new_pos = (
                monster.pos[0] + math.cos(angle) * monster_speed,
                monster.pos[1] + math.sin(angle) * monster_speed,
            )
            if not self.level.wall_collision(new_pos):
                if not self.level.monster_collisions(
                    new_pos, radius=0.5, ignore=[monster]
                ):
                    monster.pos = new_pos

    def animate_monsters(self):
        for monster in self.level.monsters:

            monster.animation.update()

    def turn_player(self):
        turn_factor = 0.03

        # turn left/right
        if self.game.pressed[pygame.K_LEFT] or self.game.pressed[pygame.K_a]:
            self.camera.angle -= turn_factor

        if self.game.pressed[pygame.K_RIGHT] or self.game.pressed[pygame.K_d]:
            self.camera.angle += turn_factor

        # cap the angle to 2pi
        if self.camera.angle > PI_2:
            self.camera.angle -= PI_2

        if self.camera.angle < 0:
            self.camera.angle += PI_2

    def move_player(self):

        speed_factor = 0.05
        if self.game.pressed[pygame.K_LSHIFT]:
            speed_factor *= 2

        if pygame.K_UP in self.game.just_pressed:
            self.move_start = self.elapsed()

        if self.game.pressed[pygame.K_q]:
            # q = strafe left
            self.relocate_player(
                (
                    self.camera.pos[0]
                    + math.cos(self.camera.angle - math.pi * 0.5) * speed_factor,
                    self.camera.pos[1]
                    + math.sin(self.camera.angle - math.pi * 0.5) * speed_factor,
                )
            )

        if self.game.pressed[pygame.K_e]:
            # e = strafe right
            self.relocate_player(
                (
                    self.camera.pos[0]
                    + math.cos(self.camera.angle + math.pi * 0.5) * speed_factor,
                    self.camera.pos[1]
                    + math.sin(self.camera.angle + math.pi * 0.5) * speed_factor,
                )
            )

        if self.game.pressed[pygame.K_UP] or self.game.pressed[pygame.K_w]:
            self.relocate_player(
                (
                    self.camera.pos[0] + math.cos(self.camera.angle) * speed_factor,
                    self.camera.pos[1] + math.sin(self.camera.angle) * speed_factor,
                )
            )
        if self.game.pressed[pygame.K_DOWN] or self.game.pressed[pygame.K_s]:
            self.relocate_player(
                (
                    self.camera.pos[0] - math.cos(self.camera.angle) * speed_factor,
                    self.camera.pos[1] - math.sin(self.camera.angle) * speed_factor,
                )
            )

    def relocate_player(self, new_pos):
        if not self.level.wall_collision(new_pos):
            self.camera.pos = new_pos
        elif not self.level.wall_collision((new_pos[0], self.camera.pos[1])):
            self.camera.pos = (new_pos[0], self.camera.pos[1])
        elif not self.level.wall_collision((self.camera.pos[0], new_pos[1])):
            self.camera.pos = (self.camera.pos[0], new_pos[1])

    def update_player(self):

        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        self.turn_player()
        self.move_player()

    def draw(self):
        floor_color = (120, 120, 120)
        ceiling_color = (160, 160, 165)
        self.display.fill(ceiling_color)
        pygame.draw.rect(
            self.display,
            floor_color,
            (0, self.render_height // 2, self.render_width, self.render_height // 2),
        )

        self.draw_walls()
        self.draw_objects()
        self.draw_map()
        self.draw_weapon()

        # scale the display to the game window size
        if self.render_scale > 1:
            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
        else:
            self.screen.blit(self.display, (0, 0))

    def draw_weapon(self):
        if self.weapon == "pistol":
            self.draw_pistol()
        elif self.weapon == "rifle":
            self.draw_rifle()

    def draw_rifle(self):

        x = self.render_width // 2 - self.assets["rifle"].get_width() // 2

        y = self.render_height - self.assets["rifle"].get_height()

        if self.game.pressed[pygame.K_UP]:

            traversal = 3
            speed = 10

            if self.game.pressed[pygame.K_LSHIFT]:
                traversal = 5
                speed = 15

            shift = traversal + traversal * math.sin(
                (self.elapsed() - self.move_start) * speed
            )

            y += shift

        self.display.blit(self.assets["rifle"], (x, y))

    def draw_pistol(self):

        x = self.render_width // 3 * 2

        y = self.render_height - self.assets["pistol"].get_height()

        if self.game.pressed[pygame.K_UP]:

            traversal = 3
            speed = 10

            if self.game.pressed[pygame.K_LSHIFT]:
                traversal = 5
                speed = 15

            shift = traversal + traversal * math.sin(
                (self.elapsed() - self.move_start) * speed
            )

            y += shift

        self.display.blit(self.assets["pistol"], (x, y))

    def draw_objects(self):
        # make a list of objects in our fov
        render_objects = []

        # combine level objects and monsters into one list to check

        combined = self.level.level_objects + self.level.monsters

        for obj in combined:
            rads = math.atan2(
                obj.pos[1] - self.camera.pos[1], obj.pos[0] - self.camera.pos[0]
            )
            rd = abs(radian_diff(self.camera.angle, rads))
            # self.log(f"Angle: {angle}, Angle Diff: {angle_diff}")
            if abs(rd) < self.fov_rad_half or abs(rd) > PI_2 - self.fov_rad_half:
                distance = line_distance(*self.camera.pos, *obj.pos)

                # check the distance to the wall at this angle
                # to see if it's the object is closer than the wall
                # first compute which slice the object is in
                x = self.convert_radians_to_slice(rads)

                if distance < self.distances[x] and distance > 0.25:
                    render_objects.append((distance, rads, x, obj))

        # sort the objects by distance  so we can render them in the correct order
        render_objects.sort(key=lambda x: x[0], reverse=True)

        # blit the object to the display in the correct order
        for o in render_objects:
            d = o[0]
            r = o[1]
            x = o[2]
            obj = o[3]
            scale = 1 / (d / 2)
            obj_img = obj.img()

            scaled = pygame.transform.scale(
                obj_img,
                (
                    int(obj_img.get_width() * scale),
                    int(obj_img.get_height() * scale),
                ),
            )

            wall_height = (1 / d) * self.render_height
            wall_height = self.constrain(wall_height, 5, self.render_height * 4)
            wh_top = (self.render_height // 2) - (wall_height // 2)
            wh_bottom = (self.render_height // 2) + (wall_height // 2)
            left = x - scaled.get_width() // 2
            top = wh_bottom - scaled.get_height()
            # draw the object at bottom of the wall
            if obj.type == "chandelier":
                top = wh_top
            self.display.blit(scaled, (left, top))

            # uncomment the line below to draw a green pixel
            # where the bottom center of the sprite was determined to be
            # self.display.set_at((x, wh_bottom), (0, 255, 0))

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

        # determine which texture to use
        # if the wall we intersected was type 1 use bricks
        # if the wall is type 2 use the flag

        wall_texture = self.assets["bricks"]
        if self.wall_textures[x] == 2:
            wall_texture = self.assets["flag"]
        elif self.wall_textures[x] == 3:
            wall_texture = self.assets["wood"]
        # determine the position of the slice we need to draw
        wp_x = self.wall_points[x, 0]
        wp_y = self.wall_points[x, 1]
        texture_x = abs(wp_x - int(wp_x)) + abs(wp_y - int(wp_y))
        texture_x = self.constrain(texture_x, 0, 1)
        texture_x = int(texture_x * wall_texture.get_width() - 1)

        wall_height = (1 / distance) * self.render_height
        wall_height = self.constrain(wall_height, 5, self.render_height * 4)
        top = (self.render_height // 2) - (wall_height // 2)

        self.display.blit(
            pygame.transform.scale(
                wall_texture.subsurface(texture_x, 0, 1, wall_texture.get_height()),
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

                    # extend the wall point by 0.001 along it's
                    # angle and then sample the texture of the
                    # wall at that point
                    x = intersection[0] + math.cos(self.rads[i]) * 0.001
                    y = intersection[1] + math.sin(self.rads[i]) * 0.001
                    x = math.floor(x)
                    y = math.floor(y)
                    texture = self.level.map[x, y]

                    self.wall_textures[i] = texture
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
    def __init__(self, level_number, scene):
        self.scene = scene
        map_path = f"raycaster/maps/{level_number}.png"

        # check if the map file exists
        if not os.path.exists("assets/" + map_path):
            raise FileNotFoundError(f"Map file {map_path} not found")

        self.pos_camera_start = (0, 0)
        self.level_objects = []
        self.monster_spawners = []
        self.monsters = []
        self.map_data = load_tpng(map_path)

        self.map_height = self.map_data.get_height()
        self.map_width = self.map_data.get_width()

        self.map = np.zeros((self.map_width, self.map_height))

        self.parse_map()

    def parse_map(self):
        self.map = np.zeros((self.map_width, self.map_height))
        for x in range(self.map_width):
            for y in range(self.map_height):
                pixel_color = self.map_data.get_at((x, y))

                # white is a red brick wall
                if pixel_color == (255, 255, 255):
                    self.map[x, y] = 1

                # blue is the flag wall
                elif pixel_color == (0, 0, 255):
                    self.map[x, y] = 2

                # brown is the wood wall (185, 122, 87)
                elif pixel_color == (185, 122, 87):
                    self.map[x, y] = 3

                # red is player starting position
                elif pixel_color == (255, 0, 0):
                    self.pos_camera_start = (x, y)

                # green is a tree
                elif pixel_color == (0, 255, 0):
                    self.level_objects.append(
                        LevelObject((x + 0.5, y + 0.5), "tree", self.scene)
                    )

                # orange is a monster spawner
                elif pixel_color == (255, 127, 39):
                    self.level_objects.append(
                        LevelObject((x + 0.5, y + 0.5), "telepad", self.scene)
                    )
                    self.monster_spawners.append((x, y, "toad", self.scene))

                # yellow is a chandelier
                elif pixel_color == (255, 242, 0):
                    self.level_objects.append(
                        LevelObject((x + 0.5, y + 0.5), "chandelier", self.scene)
                    )

                elif pixel_color == (0, 0, 0):
                    # empty space
                    pass
                else:
                    print("Unknown color", pixel_color)
                    pass

    def spawn_monsters(self, amount=1):

        # spawn from 1 to the amount of spawners
        spawn_count = constrain(amount, 1, len(self.monster_spawners))

        avail_spawns = self.monster_spawners.copy()

        for _ in range(spawn_count):
            random_spawn = random.choice(avail_spawns)
            avail_spawns.remove(random_spawn)
            mob = Monster(
                pos=random_spawn[:2],
                type=random_spawn[2],
                action="walk",
                scene=self.scene,
            )
            # increment the pos by 0.5, 0.5 to center it in the tile it is spawned in
            mob.pos = (mob.pos[0] + 0.5, mob.pos[1] + 0.5)

            # check that this does not spawn within a tile of an existing monster
            if not self.monster_collisions(mob.pos, ignore=[mob]):

                self.monsters.append(mob)

    def wall_collision(self, pos=(0, 0)) -> bool:

        x = int(pos[0])
        y = int(pos[1])
        return self.map[x, y] > 0

    def monster_collisions(
        self, pos=(0, 0), radius: float = 1.0, ignore: None | list = None
    ) -> bool:

        if ignore is None:
            ignore = []

        for monster in self.monsters:
            if monster in ignore:
                continue

            distance = math.sqrt(
                (pos[0] - monster.pos[0]) ** 2 + (pos[1] - monster.pos[1]) ** 2
            )
            if distance < radius:
                return True

        return False


class LevelObject:
    def __init__(self, pos=(0, 0), type="tree", scene: Scene = None):
        self.scene = scene
        self.pos = pos
        self.type = type

    def img(self):
        return self.scene.assets[self.type]


class Monster:
    def __init__(
        self, pos=(0, 0), type="toad", action: str = "walk", scene: Scene = None
    ):
        # set default values for the monster
        self.action = ""  # TODO: look at making action private
        self.animation = None

        # store the variables and references
        self.scene = scene
        self.pos = pos
        self.type = type

        # set the action for the monster
        self.set_action(action)

    def img(self):
        return self.animation.img()

    def set_action(self, action: str):
        if self.action != action:
            self.action = action
            self.animation = self.scene.assets[f"{self.type}/{self.action}"].copy()
            self.animation.reset()


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


# load a single image
def load_image_alpha(path):
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    return img


# load all images in a directory
def load_images_alpha(path):
    images = []

    for img_name in sorted(
        os.listdir(BASE_IMAGE_PATH + path)
    ):  # sorted is used for OS interoperability
        images.append(load_image_alpha(path + "/" + img_name))

    return images


# a method that will return the difference in radians between two angles
# in radians
def radian_diff(a, b):
    return (a - b + math.pi) % (2 * math.pi) - math.pi
