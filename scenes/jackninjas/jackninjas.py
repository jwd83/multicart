import math
import random
import sys
import pygame
import os
from scene import Scene
from .scripts.entities import PhysicsEntity, Enemy, Player
from .scripts.utils import load_image, load_images, Animation
from .scripts.tilemap import Tilemap
from .scripts.clouds import Clouds
from .scripts.particle import Particle
from .scripts.spark import Spark
from .scripts.projectile import Projectile
from typing import List


class JackNinjas(Scene):
    def __init__(self, game):
        super().__init__(game)

        # this will store the list of items the player has collected
        self.inventory = []

        # we will render at 320x180 and then scale it up
        self.display = pygame.Surface((320, 180), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 180))

        self.clock = pygame.time.Clock()

        self.play_music("sounds/ambience.wav")
        self.movement = [False, False]

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "collectibles": load_images("tiles/collectibles"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), img_dur=8),
            "enemy/run": Animation(load_images("entities/enemy/run"), img_dur=4),
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
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
            "glaive": load_image("tiles/collectibles/1.png"),
            "heart": load_image("heart8.png"),
        }

        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.player = Player(self, (75, 75), (8, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.load_level(self.level)
        # setup screenshake variables
        self.screen_shake = 0

    def load_level(self, map_id):

        self.tilemap.load("assets/jackninjas/maps/" + str(map_id) + ".json")

        # setup leaf spawners
        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            self.leaf_spawners.append(
                pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            )

        self.collectibles = []
        extract = self.tilemap.extract([("collectibles", 0), ("collectibles", 1)])
        for collectible in extract:
            self.collectibles.append(collectible)

        self.enemies: List[PhysicsEntity] = []
        extract = self.tilemap.extract([("spawners", 0), ("spawners", 1)])
        for spawner in extract:
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))

        self.projectiles: List[Projectile] = []
        self.particles = []
        self.sparks = []
        # setup our pseudo camera
        self.scroll = [0, 0]
        self.dead = 0

        self.transition = -30

    def perform_quit(self):
        pygame.quit()
        sys.exit()

    def update(self):

        # need to rewrite the hell out of this one...
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        # movement input
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

        if pygame.K_x in self.game.just_pressed:
            self.player.dash()

        if self.game.pressed[pygame.K_z]:
            self.player.throw_glaive()

        # if pygame.K_z in self.game.just_pressed:
        #     self.player.throw_glaive()

        # jack's optional q code for testing
        # if pygame.K_q in self.game.just_pressed:
        #     self.inventory.append("double_jump")
        #     self.inventory.append("glaive")

        # TODO - rewrite the joystick/gamepad input logic.

    def draw(self):
        self.display.fill((0, 0, 0, 0))  # pure transparency
        self.display_2.blit(self.assets["background"], (0, 0))

        self.screen_shake = max(
            0, self.screen_shake - 1
        )  # decrement the screen shake counter by one each frame

        # check if all enemies have been killed
        if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
                self.level = min(
                    self.level + 1, len(os.listdir("assets/jackninjas/maps")) - 1
                )
                self.load_level(self.level)

        if self.transition < 0:
            self.transition += 1

        if self.dead:
            self.dead += 1
            if self.dead >= 10:
                self.transition = min(30, self.transition + 1)
            if self.dead > 40:
                self.load_level(self.level)  # this will clear the dead counter

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
        self.clouds.render(self.display_2, offset=render_scroll)

        # draw our tilemap
        self.tilemap.render(self.display, offset=render_scroll)

        # draw our off grid collectibles
        for collectible in self.collectibles:

            # check if player is colliding with collectible
            if self.player.rect().colliderect(
                pygame.Rect((collectible["pos"][0], collectible["pos"][1]), (16, 16))
            ):
                self.collectibles.remove(collectible)
                if collectible["variant"] == 0:
                    self.inventory.append("double_jump")
                elif collectible["variant"] == 1:
                    self.inventory.append("glaive")

            self.display.blit(
                self.assets["collectibles"][collectible["variant"]],
                (
                    collectible["pos"][0] - render_scroll[0],
                    collectible["pos"][1]
                    - render_scroll[1]
                    + 2.5 * math.sin(self.elapsed() * 4),
                ),
            )

        # draw our enemies
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap)
            enemy.render(self.display, offset=render_scroll)
            if kill:
                self.enemies.remove(enemy)

        for projectile in self.projectiles.copy():
            # adjust the x coordinate by the direction of the bullet
            projectile.pos[0] += projectile.velocity
            # increment the projectile's timer
            projectile.timer += 1

            if projectile.variant == "bullet":
                img = self.assets["projectile"]
            elif projectile.variant == "glaive":
                img = self.assets["glaive"]

            if projectile.flip:
                img = pygame.transform.flip(img, True, False)

            blt_position = (
                (
                    projectile.pos[0] - img.get_width() / 2 - render_scroll[0],
                    projectile.pos[1] - img.get_height() / 2 - render_scroll[1],
                ),
            )

            if projectile.variant == "bullet":
                self.display.blit(img, blt_position)
            elif projectile.variant == "glaive":
                self.blitRotateCenter(
                    image=img,
                    topleft=blt_position,
                    angle=self.elapsed() * projectile.rotation,
                    destination_surface=self.display_2,
                )

            if self.tilemap.solid_check(projectile.pos):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(
                        Spark(
                            projectile.pos,
                            random.random()
                            - 0.5
                            + (math.pi if projectile.velocity > 0 else 0),
                            2 + random.random(),
                        )
                    )
            elif projectile.timer > projectile.timeout:
                self.projectiles.remove(projectile)
            else:
                # projectile collision detection with entities starts here

                # enemy collision detection
                if projectile.variant == "glaive":

                    projectile_size = 14 / 2
                    projectile_rect = pygame.Rect(
                        (
                            projectile.pos[0] - projectile_size,
                            projectile.pos[1] - projectile_size,
                        ),
                        (projectile_size * 2, projectile_size * 2),
                    )

                    for enemy in self.enemies.copy():
                        if enemy.rect().colliderect(projectile_rect):
                            # don't remove the projectile if it's already been removed by another enemy
                            # on a different iteration of this loop (ie, it hit more than 1 enemy, it would
                            # already be removed)
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)
                            self.enemies.remove(enemy)
                            self.screen_shake = max(8, self.screen_shake)

                # player collision detection with projectile of variant "bullet"
                if projectile.variant == "bullet":
                    if abs(self.player.dashing) < 50:  # fast part of dash is over
                        if self.player.rect().collidepoint(projectile.pos):
                            # player got hit
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.screen_shake = max(
                                30, self.screen_shake
                            )  # set it to 16 if it's lower
                            for _ in range(30):
                                angle = random.random() * math.pi
                                speed = random.random() * 5
                                self.sparks.append(
                                    Spark(
                                        self.player.rect().center,
                                        angle,
                                        2 + random.random(),
                                    )
                                )
                                self.particles.append(
                                    Particle(
                                        self,
                                        "particle",
                                        self.player.rect().center,
                                        velocity=(
                                            math.cos(angle + math.pi) * speed * 0.5,
                                            math.sin(angle * math.pi) * speed * 0.5,
                                        ),
                                        frame=random.randint(0, 7),
                                    )
                                )

        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

        # update and draw our player
        if not self.dead:
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

        # outline what has been drawn so far
        display_mask = pygame.mask.from_surface(self.display)
        display_silhouette = display_mask.to_surface(
            setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0)
        )

        for silhouette_offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            self.display_2.blit(display_silhouette, silhouette_offset)

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

        # handle our transition effect
        if self.transition:  # when non-zero
            t_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(
                t_surf,
                (255, 255, 255),
                (self.display.get_width() // 2, self.display.get_height() // 2),
                (30 - abs(self.transition)) * 8,
            )
            t_surf.set_colorkey((255, 255, 255))
            self.display.blit(t_surf, (0, 0))

        self.display_2.blit(self.display, (0, 0))

        # calculate our screen shake offset
        shake_offset = (
            random.random() * self.screen_shake - self.screen_shake / 2,
            random.random() * self.screen_shake - self.screen_shake / 2,
        )

        # FRAME COMPLETE
        # we finished drawing our frame, lets render it to the screen
        self.screen.blit(
            pygame.transform.scale(self.display_2, self.screen.get_size()), shake_offset
        )

        # draw the user interface
        self.draw_user_interface()

    def draw_user_interface(self):
        # render UI on top of the completed frame
        self.screen.blit(self.assets["heart"], (4, 4))

        # draw a health bar for the player next to the heart
        health_width = max(0, self.player.health)

        if health_width:
            pygame.draw.rect(
                surface=self.screen,
                color=(255, 0, 0),
                rect=(16, 4, health_width, 8),
            )
