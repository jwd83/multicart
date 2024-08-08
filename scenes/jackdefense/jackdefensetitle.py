import pygame
from scene import Scene
from utils import Button

class JackDefenseTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.background = self.make_transparent_surface(self.screen.get_size())
        self.background_image, _ = self.load_png("dark-fantasy-title.jpeg")
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())                                                          
        self.background.blit(self.background_image, (0, 0))

        self.start_button = Button(self.screen, pos = (100, 100), size = (100, 100), content = self.load_png("opengameart-jeton-bleu.png")[0])

    def update(self):

        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "GameSelect"
            return
        
    def draw(self):
        if self.active:
            # draw a black background
            self.screen.fill((0, 0, 0))

            # draw the background
            self.screen.blit(self.background, (0, 0))

            # Draw our start button
            if self.start_button.draw(): 
                print('Start button clicked!')

