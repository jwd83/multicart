import math
import random
import sys
import pygame
from scene import Scene
from .scripts.entities import PhysicsEntity, Player
from .scripts.utils import load_image, load_images, Animation
from .scripts.tilemap import Tilemap
from .scripts.clouds import Clouds
from .scripts.particle import Particle


class JackNinjas(Scene):
    def __init__(self, game):
        super().__init__(game)

        # we will render at 320x180 and then scale it up by 4x
        self.display = pygame.Surface((320, 180))

        self.clock = pygame.time.Clock()

        self.play_music("sounds/ambience.wav")

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=8),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/fall": Animation(load_images("entities/player/fall")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(
                load_images("entities/player/wall_slide"), img_dur=5
            ),
            "particle/leaf": Animation(
                load_images("particles/leaf"), img_dur=12, loop=False
            ),
            "particle/particle": Animation(
                load_images("particles/particle"), img_dur=6, loop=False
            ),
        }
        # print our loaded assets
        print(self.assets)

        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.player = Player(self, (75, 75), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        try:
            self.tilemap.load("assets/jackninjas/map.json")
        except FileNotFoundError:
            pass

        self.movement = [False, False]

        # setup our pseudo camera
        self.scroll = [0, 0]

        # setup leaf spawners
        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            self.leaf_spawners.append(
                pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            )
        self.particles = []

    def perform_quit(self):
        pygame.quit()
        sys.exit()

    def update(self):

        # need to rewrite the hell out of this one...
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        # if the user presses escape or F5 key, quit the event loop.
        if (
            pygame.K_LEFT in self.game.just_pressed
            or pygame.K_a in self.game.just_pressed
        ):
            self.movement[0] = True
        if (
            pygame.K_RIGHT in self.game.just_pressed
            or pygame.K_d in self.game.just_pressed
        ):
            self.movement[1] = True

        if (
            pygame.K_LEFT in self.game.just_released
            or pygame.K_a in self.game.just_released
        ):
            self.movement[0] = False
        if (
            pygame.K_RIGHT in self.game.just_released
            or pygame.K_d in self.game.just_released
        ):
            self.movement[1] = False

        if (
            pygame.K_SPACE in self.game.just_pressed
            or pygame.K_w in self.game.just_pressed
            or pygame.K_UP in self.game.just_pressed
        ):
            self.player.jump()

        if (pygame.K_x in self.game.just_pressed):
            self.player.dash()

        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))

        # TODO - rewrite the joystick/gamepad input logic.

        return

        # get our events so windows thinks we are responding
        for event in pygame.event.get():

            # handle controller mappings
            # dpad up is 11
            # left is 13
            # right is 14

            # handle controller button down
            if event.type == pygame.JOYBUTTONDOWN:
                print(event)

                # jump
                if event.button == 1:
                    self.player.jump()

                # left
                if event.button == 13:
                    self.movement[0] = True

                # right
                if event.button == 14:
                    self.movement[1] = True

            # handle controller button up
            if event.type == pygame.JOYBUTTONUP:
                print(event)
                # left
                if event.button == 13:
                    self.movement[0] = False

                # right
                if event.button == 14:
                    self.movement[1] = False

    def draw_background(self):
        # let's go for a sky blue
        # self.display.fill((15,220,250))
        self.display.blit(self.assets["background"], (0, 0))

    def draw(self):
        self.draw_background()

        # adjust camera position
        self.scroll[0] += (
            self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]
        ) / 30
        self.scroll[1] += (
            (self.player.rect().centery - 20)
            - self.display.get_height() / 2
            - self.scroll[1]
        ) / 8
        # calculate integer scroll for rendering to fix jitter
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        # draw our clouds
        self.clouds.update()
        self.clouds.render(self.display, offset=render_scroll)

        # draw our tilemap
        self.tilemap.render(self.display, offset=render_scroll)

        # update and draw our player
        self.player.render(self.display, offset=render_scroll)

        # spawn leaf particles
        for rect in self.leaf_spawners:
            if random.random() * 50000 < rect.width * rect.height:
                pos = (
                    rect.x + random.random() * rect.width,
                    rect.y + random.random() * rect.height,
                )
                self.particles.append(
                    Particle(
                        self,
                        "leaf",
                        pos,
                        velocity=[-0.1, 0.3],
                        frame=random.randint(0, 100),
                    )
                )

        # handle particle effects
        for particle in self.particles.copy():
            kill = particle.update()
            if particle.type == "leaf":
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            particle.render(self.display, offset=render_scroll)
            if kill:
                self.particles.remove(particle)

        # FRAME COMPLETE
        # we finished drawing our frame, lets render it to the screen and
        # get our input events ready for the next frame and sleep for a bit
        self.screen.blit(
            pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
        )
