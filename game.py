import os
import pygame
import settings
from scene import Scene
import scenes
import sys


class Game:
    def __init__(self):
        # set the quit flag to false at the start
        self.quit = False
        self.pressed = []
        self.just_pressed = []
        self.sfx = {}
        self.volume_music = 100
        self.volume_effects = 100
        self.winner = None

        # initialize pygame
        pygame.init()
        pygame.mixer.init()

        # load all sounds in assets/sounds as sound effects
        for sound in os.listdir("assets/sounds"):
            load_sound = False
            if (
                sound.endswith(".wav")
                or sound.endswith(".ogg")
                or sound.endswith(".mp3")
            ):
                load_sound = True

            if load_sound:
                sound_name = sound.split(".")[0]
                self.sfx[sound_name] = pygame.mixer.Sound("assets/sounds/" + sound)

        # create a window
        self.screen: pygame.Surface = pygame.display.set_mode(
            settings.RESOLUTION, pygame.FULLSCREEN | pygame.SCALED
        )
        pygame.display.set_caption(settings.TITLE)

        # create a pygame clock to limit the game to 60 fps
        self.clock = pygame.time.Clock()

        # create a stack for scenes to be updated and drawn
        # and add the title scene to the stack
        self.scene = []  # type: list[Scene]
        self.scene.append(self.load_scene(settings.SCENE_START))

        # create variables to handle scene changes
        self.scene_replace = None
        self.scene_push = None
        self.scene_pop = None

    def run(self):
        self.debug_scene = scenes.Debug(self)

        while not self.quit:

            # process scene change requests (if any)
            self.change_scenes()

            # handle events and input
            self.get_events_and_input()

            # set all scenes to inactive except the top scene in the stack
            for scene in self.scene:
                scene.active = False
            self.scene[-1].active = True

            # process update for the top scene in the stack
            self.scene[-1].update()

            # draw all scenes in the stack from bottom to top
            for scene in self.scene:
                scene.draw()

            # draw the debug panel
            if settings.DEBUG:
                self.debug_scene.update()
                self.debug_scene.draw()

            # update the display
            pygame.display.flip()

            # limit the game to 60 fps
            self.clock.tick(settings.FPS)

        # quit the game
        print("quit=True")
        pygame.quit()
        sys.exit()

    def get_events_and_input(self):
        # get input
        self.pressed = pygame.key.get_pressed()
        self.just_pressed = []

        # get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                self.just_pressed.append(event.key)

        # check for escape key to quit
        if pygame.K_ESCAPE in self.just_pressed:
            pass
            # self.scene_pop = True
            # self.quit = True

        # check for F11 to toggle the debug setting
        if pygame.K_F11 in self.just_pressed:
            settings.DEBUG = not settings.DEBUG

    def valid_scene_name(self, scene: str):
        return scene in dir(scenes)

    def change_scenes(self):
        # check for scene changes

        # start off by looking for a replacement scene to rebuild the stack
        if self.scene_replace is not None:
            print("scene_replace: " + self.scene_replace)
            if self.valid_scene_name(self.scene_replace):
                self.scene = []
                self.scene.append(self.load_scene(self.scene_replace))
            self.scene_replace = None

        # next, look for a pop request to clear the stack
        if self.scene_pop is not None:
            if len(self.scene) > 1:
                # if scene pop was given an integer, pop that many scenes
                # otherwise, pop only one scene
                if isinstance(self.scene_pop, int):
                    print("scene_pop: " + str(self.scene_pop))
                    if self.scene_pop >= len(self.scene):
                        print("WARNING: Cannot pop more scenes than exist! Exiting!")
                        self.quit = True
                    else:
                        for _ in range(self.scene_pop):
                            self.scene.pop()
                else:
                    print("scene_pop: 1")
                    self.scene.pop()
            else:
                print("WARNING: Cannot pop last scene! Exiting!")
                self.quit = True
            self.scene_pop = None

        if self.scene_push is not None:
            if self.valid_scene_name(self.scene_push):
                print("scene_push: " + self.scene_push)
                self.scene.append(self.load_scene(self.scene_push))
            else:
                print(
                    "scene_push: " + self.scene_push + ", WARNING: Invalid scene name!"
                )
            self.scene_push = None

    def load_scene(self, scene: str):
        print("load_scene: " + scene)

        # check if the string passed in matches the name of a class in the scenes module
        if scene in dir(scenes):
            return eval("scenes." + scene + "(self)")
