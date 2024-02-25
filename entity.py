from vector2 import Vector2
import scene


class Entity:
    def __init__(self, scene: scene.Scene, sprite=None):
        self.scene = scene
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        if sprite is not None:
            self.sprite, _ = self.scene.load_png(sprite)
        else:
            self.sprite = self.scene.make_transparent_surface((10, 10))
            self.sprite.fill((255, 255, 255))

    def update(self):
        pass

    def draw(self):
        self.scene.screen.blit(self.sprite, self.position.pos())
