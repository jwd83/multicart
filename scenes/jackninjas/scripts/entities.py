import math
import random
import pygame
from .particle import Particle
from scene import Scene
from .spark import Spark
from .projectile import Projectile

GRAVITY = 0.1
MAX_FALL_SPEED = 5
JUMP_WALL_REBOUND = 3.3
JUMP_STANDARD = 3
JUMP_WALL = 2.5


class PhysicsEntity:
    def __init__(self, scene: Scene, e_type, pos, size):
        self.scene = scene
        self.type = e_type

        # create a new list so we don't modify or share with another entity
        self.pos = list(pos)
        # x position is first element in pos list
        # y position is second element in pos list

        # create a new list so we don't modify or share with another entity
        self.size = list(size)
        self.velocity = [0, 0]
        self.collisions = {"up": False, "down": False, "left": False, "right": False}
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

        self.last_movement = [0, 0]

    def max_jumps(self) -> int:
        return 1

    def set_action(self, action):

        # if we are in the air and have not jumped yet then we should deduct a jump for falling off a ledge
        if action == "fall":
            if self.jumps == self.max_jumps():
                self.jumps -= 1

        # only change the animation if it's different
        if action != self.action:
            self.action = action
            self.animation = self.scene.assets[self.type + "/" + self.action].copy()
            self.animation.frame = 0

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        frame_movement = [
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        ]

        # handle x axis movement
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # if we are moving right and collided with a tile
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        # handle y axis movement
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # if we are moving down and collided with a tile
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y

        # apply gravity
        self.velocity[1] = min(MAX_FALL_SPEED, self.velocity[1] + GRAVITY)

        # reset y velocity if collided up or down
        if self.collisions["up"] or self.collisions["down"]:
            self.velocity[1] = 0

        self.last_movement = movement
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (
                self.pos[0] - offset[0] + self.anim_offset[0],
                self.pos[1] - offset[1] + self.anim_offset[1],
            ),
        )


class Enemy(PhysicsEntity):
    def __init__(self, scene: Scene, pos, size):
        super().__init__(scene, "enemy", pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check(
                (self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)
            ):
                if self.collisions["left"] or self.collisions["right"]:
                    self.flip = not self.flip
                else:
                    movement = (
                        movement[0] - 0.5 if self.flip else movement[0] + 0.5,
                        movement[1],
                    )
            else:
                self.flip = not self.flip

            self.walking = max(0, self.walking - 1)

            if not self.walking:
                dis = (
                    self.scene.player.pos[0] - self.pos[0],
                    self.scene.player.pos[1] - self.pos[1],
                )

                # check if the player is in range vertically
                if abs(dis[1]) < 16:
                    # check if we are facing the player
                    shoot = False
                    shoot_mul = 1
                    shoot_offset = 7
                    shoot_speed = 1.5

                    # determine if we shoot
                    if self.flip and dis[0] < 0:
                        shoot = True
                        shoot_mul = -1
                    elif not self.flip and dis[0] > 0:
                        shoot = True

                    # take the shot
                    if shoot:
                        self.scene.projectiles.append(
                            Projectile(
                                pos=[
                                    self.rect().centerx + shoot_offset * shoot_mul,
                                    self.rect().centery,
                                ],
                                velocity=shoot_speed * shoot_mul,
                                timer=0,
                            )
                        )
                        for i in range(4):
                            self.scene.sparks.append(
                                Spark(
                                    self.scene.projectiles[-1].pos,
                                    random.random()
                                    - 0.5
                                    + (0 if shoot_mul == 1 else math.pi),
                                    2 + random.random(),
                                )
                            )

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement)

        if movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        if abs(self.scene.player.dashing) >= 50:
            if self.rect().colliderect(self.scene.player.rect()):
                self.scene.screen_shake = max(16, self.scene.screen_shake)

                # generate the primary explosion
                for _ in range(30):
                    angle = random.random() * math.pi
                    speed = random.random() * 5
                    self.scene.sparks.append(
                        Spark(self.rect().center, angle, 2 + random.random())
                    )
                    self.scene.particles.append(
                        Particle(
                            self.scene,
                            "particle",
                            self.rect().center,
                            velocity=(
                                math.cos(angle + math.pi) * speed * 0.5,
                                math.sin(angle * math.pi) * speed * 0.5,
                            ),
                            frame=random.randint(0, 7),
                        )
                    )

                # add 2 more big sparks that go left and right
                self.scene.sparks.append(
                    Spark(self.rect().center, 0, 5 + random.random())
                )
                self.scene.sparks.append(
                    Spark(self.rect().center, math.pi, 5 + random.random())
                )

                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf=surf, offset=offset)

        if self.flip:
            surf.blit(
                pygame.transform.flip(self.scene.assets["gun"], True, False),
                (
                    self.rect().centerx
                    - 4
                    - self.scene.assets["gun"].get_width()
                    - offset[0],
                    self.rect().centery - offset[1],
                ),
            )
        else:
            surf.blit(
                self.scene.assets["gun"],
                (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]),
            )


class Player(PhysicsEntity):
    def __init__(self, scene: Scene, pos, size):
        super().__init__(scene, "player", pos, size)

        self.jumps = self.max_jumps()
        self.air_time = 0
        self.space_jump = False
        self.wall_slide = False
        self.dashing = 0
        self.dash_ready = True
        self.throw_last = self.scene.elapsed()
        self.throw_cooldown = 0.25
        self.health = 100

    def throw_glaive(self) -> bool:
        if self.has("glaive"):
            t = self.scene.elapsed()
            if t - self.throw_last > self.throw_cooldown:
                self.throw_last = t

                p_rotation_speed = -1000 if self.flip else 1000
                p_velocity = -4 if self.flip else 4

                self.scene.projectiles.append(
                    Projectile(
                        pos=self.rect().center,
                        velocity=p_velocity,
                        variant="glaive",
                        timer=0,
                        rotation=p_rotation_speed,
                        flip=not self.flip,
                    )
                )

    def max_jumps(self) -> int:
        return 2 if self.has("double_jump") else 1

    def has(self, item: str) -> bool:
        return item in self.scene.inventory

    def render(self, surf, offset=(0, 0)):
        # hide the player for the first 10 frames of the dash
        if abs(self.dashing) <= 50:
            super().render(surf, offset)
        frame = self.animation.img().copy()

        if self.dash_ready:
            # swap all the red and green color channel values
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):

                    r, g, b, a = frame.get_at((x, y))

                    frame.set_at((x, y), (g, r, b, a))

        if self.jumps == 1:
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):

                    r, g, b, a = frame.get_at((x, y))

                    frame.set_at((x, y), (r | b, g, b, a))

        if self.jumps == 0:
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):

                    r, g, b, a = frame.get_at((x, y))

                    frame.set_at((x, y), (r | b, g | b, b, a))

        surf.blit(
            pygame.transform.flip(frame, self.flip, False),
            (
                self.pos[0] - offset[0] + self.anim_offset[0],
                self.pos[1] - offset[1] + self.anim_offset[1],
            ),
        )

    def dash(self):
        # old check was
        # if not self.dashing
        if self.dash_ready:
            self.dash_ready = False
            self.scene.play_sound("dash")
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

    def jump(self):
        if self.wall_slide:
            self.jumps = max(0, self.jumps - 1)
            # wall jump has less velocity
            self.velocity[1] = -JUMP_WALL
            self.air_time = 5
            # spring off the wall
            if self.collisions["right"]:
                self.velocity[0] = -JUMP_WALL_REBOUND
            else:
                self.velocity[0] = JUMP_WALL_REBOUND
            self.scene.play_sound("jump")
            return True  # jump successful

        elif self.jumps or self.space_jump:
            if self.velocity[1] >= 0:
                self.velocity[1] = -JUMP_STANDARD
                self.jumps -= 1
                self.scene.play_sound("jump")
                return True  # jump successful

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        # handle wall slide
        self.wall_slide = False

        # check for floor collision
        self.air_time += 1

        # if we fall for too long we die
        if self.air_time > 240:
            if not self.scene.dead:
                self.scene.screen_shake = max(16, self.scene.screen_shake)
            self.scene.dead += 40
            self.air_time = 0

        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = self.max_jumps()
            self.dash_ready = True
        else:
            # we are in the air, check if we are colliding with a wall
            if (
                self.collisions["left"] or self.collisions["right"]
            ) and self.air_time > 4:
                # if we are then we are wall sliding
                self.wall_slide = True
                # reset our jumps
                # self.jumps = self.max_jumps
                # slow our wall slide
                self.velocity[1] = min(0.25, self.velocity[1])
                # flip our sprite if necessary
                if self.collisions["right"]:
                    self.Flip = False
                else:
                    self.Flip = True

        # set our animation
        if self.wall_slide:
            self.set_action("wall_slide")
        else:
            if self.air_time > 4:
                if self.velocity[1] < 0:
                    self.set_action("jump")
                else:
                    self.set_action("fall")
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

        # apply dashing for first 10 frames of dash
        if abs(self.dashing) > 50:
            # + or - 8 depending on direction
            # divide by abs(dashing) to get 1 or -1
            self.velocity[0] = abs(self.dashing) / self.dashing * 8

            # create a particle effect
            particle_angle = random.random() * math.pi * 2  # radians
            particle_speed = random.random() * 0.5 + 0.5
            particle_velocity = [
                abs(self.dashing) / self.dashing * random.random() * 3,
                0,
            ]
            self.scene.particles.append(
                Particle(
                    self.scene,
                    "particle",
                    self.rect().center,
                    velocity=particle_velocity,
                    frame=random.randint(0, 7),
                )
            )

        # burst of particle at start and end of dash
        if abs(self.dashing) in {60, 50}:

            for _ in range(20):

                # create a particle effect
                particle_angle = random.random() * math.pi * 2  # radians
                particle_speed = random.random() * 0.5 + 0.5
                particle_velocity = [
                    math.cos(particle_angle) * particle_speed,
                    math.sin(particle_angle) * particle_speed,
                ]
                self.scene.particles.append(
                    Particle(
                        self.scene,
                        "particle",
                        self.rect().center,
                        velocity=particle_velocity,
                        frame=random.randint(0, 7),
                    )
                )

        # slow down after the dash
        if abs(self.dashing) == 50:
            self.velocity[0] *= 0.2

        # air resistance/friction to slow us down
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

        # decrement dash
        if self.dashing:
            if self.dashing > 0:
                self.dashing = max(0, self.dashing - 1)
            elif self.dashing < 0:
                self.dashing = min(0, self.dashing + 1)
