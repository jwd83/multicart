# press H to see the keybindings help menu in the scene
import os
import pygame
from scene import Scene
from .scripts.utils import load_images
from .scripts.tilemap import Tilemap


class JackNinjasEditor(Scene):
    def __init__(self, game):
        super().__init__(game)

        # set our default working_path
        self.working_path = None
        self.base_path = "assets/jackninjas/maps/"
        self.working_file = "0.json"  # default to the first level
        self.update_working_path()

        # we will render at 320x180 on a surface called display and then scale it up to our screen
        self.display = pygame.Surface((320, 180))

        self.render_scale = self.screen.get_width() / self.display.get_width()

        self.clock = pygame.time.Clock()

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "snow": load_images("tiles/snow"),
            "spawners": load_images("tiles/spawners"),
            "collectibles": load_images("tiles/collectibles"),
        }

        # attempt to load our tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        self.command_load()

        self.movement = [False, False, False, False]

        # setup our pseudo camera
        self.scroll = [0, 0]

        # start tracking mouse position
        self.mpos = pygame.mouse.get_pos()
        self.mpos = (self.mpos[0] / self.render_scale, self.mpos[1] / self.render_scale)

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.on_grid = True

        self.help_spacing = 18
        self.standard_font_size = 16
        self.standard_stroke = 0
        self.standard_font = "assets/fonts/novem___.ttf"
        self.standard_color = (255, 255, 255)

        self.show_keybindings = False
        self.keybindings_surface = self.create_keybindings_surface()

        self.commands = {
            "ls": self.command_ls,
            "wp": self.command_set_wp,
            "load": self.command_load,
            "save": self.command_save,
        }

    def command_save(self, args: str | None = None):
        self.tilemap.save(self.working_path)
        self.log("Map saved")
        self.play_sound("click")

    def command_load(self, args: str | None = None):
        # attempt to load our tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        try:
            self.tilemap.load(self.working_path)
        except FileNotFoundError:
            pass

    def command_ls(self, args: str | None = None):
        self.log("Existing map files:")

        # list all files in the base path
        for file in os.listdir(self.base_path):
            self.log(file)

    def command_set_wp(self, args: str | None = None):
        if args is None:
            self.log(f"The working path is currently set to:")
            self.log(self.working_path)
            self.log("To set a new working path, use the command:")
            self.log("wp <file>")
            self.log("Example: wp 0.json")
            return

        # trim working path to remove any leading or trailing whitespace
        file_path = args.strip()

        # check if the path is a valid filename without a folder
        if "/" in file_path or "\\" in file_path:
            self.log(f"Invalid path (directory): {file_path}")
            return

        # check that the path ends in .json
        if not file_path.endswith(".json"):
            self.log(f"Invalid path (not .json): {file_path}")
            return

        self.working_file = file_path
        self.update_working_path()
        self.log("Working path set to " + self.working_path)

    def create_keybindings_surface(self):
        keybindings_text = [
            "Keybindings for JackNinjasEditor:",
            "- ESC or F5: Return to Menu",
            "- O: Save the map from working path (wp)",
            "- L: Load the map from working path (wp)",
            "- T: Autotile",
            "- G: Toggle grid snapping",
            "- Arrow keys or WASD: Move the camera",
            "- Mouse left click: Place tile",
            "- Mouse right click: Remove tile",
            "- Mouse wheel: Change tile variant (or group with LSHIFT)",
            "- LSHIFT: Hold to modify tile group instead of variant",
            "- H: Toggle this help",
            "wp=" + self.working_path,
        ]
        surface = pygame.Surface((640, 360))
        surface.fill((0, 0, 0))
        y = 5  # Adjust starting y position
        for line in keybindings_text:
            text_surface = self.standard_text(line)
            surface.blit(text_surface, (5, y))  # Adjust x position
            y += self.help_spacing  # Adjust line spacing
        return surface

    def update_working_path(self):

        self.working_path = self.base_path + self.working_file

    def update(self):
        # mouse down checks
        if 1 in self.game.just_mouse_down:
            self.clicking = True
            if not self.on_grid:
                self.tilemap.offgrid_tiles.append(
                    {
                        "type": self.tile_list[self.tile_group],
                        "variant": self.tile_variant,
                        "pos": (
                            self.mpos[0] + self.scroll[0],
                            self.mpos[1] + self.scroll[1],
                        ),
                    }
                )

        if 3 in self.game.just_mouse_down:
            self.right_clicking = True

        # change type and variant on scroll wheel (+shift)
        if not self.shift:
            if 4 in self.game.just_mouse_down:  # mouse wheel up
                self.tile_variant = (self.tile_variant - 1) % len(
                    self.assets[self.tile_list[self.tile_group]]
                )
            if 5 in self.game.just_mouse_down:  # mouse wheel down
                self.tile_variant = (self.tile_variant + 1) % len(
                    self.assets[self.tile_list[self.tile_group]]
                )
        else:
            if 4 in self.game.just_mouse_down:  # mouse wheel up
                self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                self.tile_variant = 0
            if 5 in self.game.just_mouse_down:  # mouse wheel down
                self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                self.tile_variant = 0

        # mouse up checks
        if 1 in self.game.just_mouse_up:
            self.clicking = False

        if 3 in self.game.just_mouse_up:
            self.right_clicking = False

        # key down checks
        if (pygame.K_ESCAPE in self.game.just_pressed) or (
            pygame.K_F5 in self.game.just_pressed
        ):
            self.game.scene_push = "Menu"
        if pygame.K_o in self.game.just_pressed:
            self.command_save()
        if pygame.K_l in self.game.just_pressed:
            self.command_load()
        if pygame.K_t in self.game.just_pressed:
            self.tilemap.autotile()
        if pygame.K_g in self.game.just_pressed:
            self.on_grid = not self.on_grid
        if pygame.K_LSHIFT in self.game.just_pressed:
            self.shift = True

        if pygame.K_h in self.game.just_pressed:
            # update this with the latest working path
            self.keybindings_surface = self.create_keybindings_surface()
            self.show_keybindings = not self.show_keybindings

        # movement checks
        if self.game.pressed[pygame.K_LEFT] or self.game.pressed[pygame.K_a]:
            self.movement[0] = True
        else:
            self.movement[0] = False

        if self.game.pressed[pygame.K_RIGHT] or self.game.pressed[pygame.K_d]:
            self.movement[1] = True
        else:
            self.movement[1] = False

        if self.game.pressed[pygame.K_UP] or self.game.pressed[pygame.K_w]:
            self.movement[2] = True
        else:
            self.movement[2] = False

        if self.game.pressed[pygame.K_DOWN] or self.game.pressed[pygame.K_s]:
            self.movement[3] = True
        else:
            self.movement[3] = False

        # handle shift modifier

        if self.game.pressed[pygame.K_LSHIFT]:
            self.shift = True
        else:
            self.shift = False

    def draw(self):
        self.display.fill((0, 0, 0))

        # update movement of our camera in the map editor
        self.scroll[0] += (self.movement[1] - self.movement[0]) * 4
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 4

        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        self.tilemap.render(self.display, offset=render_scroll)

        current_tile_image = self.assets[self.tile_list[self.tile_group]][
            self.tile_variant
        ].copy()
        current_tile_image.set_alpha(100)

        self.mpos = pygame.mouse.get_pos()
        self.mpos = (self.mpos[0] / self.render_scale, self.mpos[1] / self.render_scale)
        tile_pos = (
            int((self.mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
            int((self.mpos[1] + self.scroll[1]) // self.tilemap.tile_size),
        )

        if self.on_grid:
            self.display.blit(
                current_tile_image,
                (
                    tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                    tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                ),
            )
        else:
            self.display.blit(current_tile_image, self.mpos)

        # create a tile
        if self.clicking and self.on_grid:
            self.tilemap.tilemap[str(tile_pos[0]) + ";" + str(tile_pos[1])] = {
                "type": self.tile_list[self.tile_group],
                "variant": self.tile_variant,
                "pos": tile_pos,
            }

        if self.right_clicking:
            # delete a tile
            tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]

            # delete any offgrid tiles as well
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.assets[tile["type"]][tile["variant"]]
                # calculate the hit box of the tile
                tile_rect = pygame.Rect(
                    tile["pos"][0] - self.scroll[0],
                    tile["pos"][1] - self.scroll[1],
                    tile_img.get_width(),
                    tile_img.get_height(),
                )
                if tile_rect.collidepoint(self.mpos):
                    self.tilemap.offgrid_tiles.remove(tile)

        self.display.blit(current_tile_image, (5, 5))

        # we finished drawing our frame, lets render it to the screen and
        # get our input events ready for the next frame and sleep for a bit
        self.screen.blit(
            pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
        )

        if self.show_keybindings:
            self.screen.blit(self.keybindings_surface, (0, 0))
