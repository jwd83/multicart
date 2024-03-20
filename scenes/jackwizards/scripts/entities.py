import pygame
from utils import Animation, load_tpng_folder
from scene import Scene


class Entity:
    def __init__(self, center=(0, 0), hitbox=(0, 0), scene: Scene = None):

        self.scene = scene
        self.game = scene.game
        self.frame: pygame.Surface = scene.frame
        self.center = center
        self.hitbox = hitbox
        self.action = None
        self.animations = {}
        self.facing = 'down'

    def update(self):
        self.animations[self.action + "/" + self.facing].update()

    def img(self):
        return self.animations[self.action].img()

class Player(Entity):
    def __init__(self, center=(0, 0), hitbox=(0, 0), scene: Scene = None):
        super().__init__(center=center, hitbox=hitbox, scene=scene)
        self.action = 'idle'
        self.animations = {

            # attack
            "attack/up": Animation(load_tpng_folder("jackwizards/animations/player/attack/up"), img_dur=8, loop=True),
            "attack/left": Animation(load_tpng_folder("jackwizards/animations/player/attack/left"), img_dur=8, loop=True),
            "attack/right": Animation(load_tpng_folder("jackwizards/animations/player/attack/right"), img_dur=8, loop=True),
            "attack/down": Animation(load_tpng_folder("jackwizards/animations/player/attack/down"), img_dur=8, loop=True),

            # block
            "block/up": Animation(load_tpng_folder("jackwizards/animations/player/block/up"), img_dur=15, loop=True),
            "block/left": Animation(load_tpng_folder("jackwizards/animations/player/block/left"), img_dur=15, loop=True),
            "block/right": Animation(load_tpng_folder("jackwizards/animations/player/block/right"), img_dur=15, loop=True),
            "block/down": Animation(load_tpng_folder("jackwizards/animations/player/block/down"), img_dur=15, loop=True),

            # idle
            "idle/up": Animation(load_tpng_folder("jackwizards/animations/player/idle/up"), img_dur=15, loop=True),
            "idle/left": Animation(load_tpng_folder("jackwizards/animations/player/idle/left"), img_dur=15, loop=True),
            "idle/right": Animation(load_tpng_folder("jackwizards/animations/player/idle/right"), img_dur=15, loop=True),
            "idle/down": Animation(load_tpng_folder("jackwizards/animations/player/idle/down"), img_dur=15, loop=True),

            # roll
            "roll/up": Animation(load_tpng_folder("jackwizards/animations/player/roll/up"), img_dur=15, loop=True),
            "roll/left": Animation(load_tpng_folder("jackwizards/animations/player/roll/left"), img_dur=15, loop=True),
            "roll/right": Animation(load_tpng_folder("jackwizards/animations/player/roll/right"), img_dur=15, loop=True),
            "roll/down": Animation(load_tpng_folder("jackwizards/animations/player/roll/down"), img_dur=15, loop=True),

            # swim
            "swim/up": Animation(load_tpng_folder("jackwizards/animations/player/swim/up"), img_dur=15, loop=True),
            "swim/left": Animation(load_tpng_folder("jackwizards/animations/player/swim/left"), img_dur=15, loop=True),
            "swim/right": Animation(load_tpng_folder("jackwizards/animations/player/swim/right"), img_dur=15, loop=True),
            "swim/down": Animation(load_tpng_folder("jackwizards/animations/player/swim/down"), img_dur=15, loop=True),

            # walk
            "walk/up": Animation(load_tpng_folder("jackwizards/animations/player/walk/up"), img_dur=15, loop=True),
            "walk/left": Animation(load_tpng_folder("jackwizards/animations/player/walk/left"), img_dur=15, loop=True),
            "walk/right": Animation(load_tpng_folder("jackwizards/animations/player/walk/right"), img_dur=15, loop=True),
            "walk/down": Animation(load_tpng_folder("jackwizards/animations/player/walk/down"), img_dur=15, loop=True),
        }

    def update(self):
        self.animations[self.action + "/" + self.facing].update()
        if pygame.K_RIGHT in self.game.just_pressed:
            self.facing = "right"
        if pygame.K_LEFT in self.game.just_pressed:
            self.facing = "left"
        if pygame.K_UP in self.game.just_pressed:
            self.facing = "up"
        if pygame.K_DOWN in self.game.just_pressed:
            self.facing = "down"

    def draw(self):
        # get the current animation frame
        img = self.animations[self.action + "/" + self.facing].img()

        # draw the frame centered on the current position
        self.frame.blit(img, (self.center[0] - img.get_width() // 2, self.center[1] - img.get_height() // 2))





class Monster(Entity):
    def __init__(self, center=(0, 0), hitbox=(0, 0), scene: Scene = None):
        super().__init__(center=center, hitbox=hitbox)
