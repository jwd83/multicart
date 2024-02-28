
import pygame
from scene import Scene

class SuperBallField(Scene):
    def __init__(self, game):
        super().__init__(game)

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 169, 0))

        # field layout top to bottom
        # 36 pixel top row for score/game text, then below that...
        # 20 pixels of crowd, then below that...
        # 20 pixels of sideline, then below that...
        # 260 pixels of field, then below that...
        # 24 pixels of sideline

        # draw the top black bar for the score
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, 640, 36))

        # draw the crowd made up of circles for shirts and circles for heads
        for i in range(0, 640, 20):
            for j in range(20, 36,4):
                if j % 8 == 0:
                    pygame.draw.circle(self.screen, (0, 0, 0), (i+10, j), 4)
                    pygame.draw.circle(self.screen, (255, 255, 255), (i+10, j), 3)
                    pygame.draw.rect(self.screen, (155, 0, 0), (i+5, j, 20, 4))
                else:
                    pygame.draw.circle(self.screen, (0, 0, 0), (i, j), 4)
                    pygame.draw.circle(self.screen, (255, 255, 255), (i, j), 3)
                    pygame.draw.rect(self.screen, (155, 155, 0), (i-3, j+4, 6, 4))



