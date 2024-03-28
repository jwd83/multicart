import os
import pygame
import settings
from scene import Scene
import scenes
import sys
import asyncio
import configparser
import time


class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.mixer.init()
        pygame.joystick.init()

        # hardcode some default values

        self.__DEFAULT_VOLUME = 50

        # game specific variables and references
        # create a placeholder references to scenes that need to be accessed like jackwizards
        # todo: for jw and others we should update our load function to purge this reference
        # back to None if it leaves the scene stack so it can be picked up by the garbage collector
        # instead of waiting for it to be reassigned later and for the last reference to
        # an instance of jack wizards to be removed.
        self.four_jacks_easy = True
        self.jw = None

        # set the quit flag to false at the start
        self.quit = False
        self.pressed = []
        self.just_pressed = []
        self.just_released = []
        self.just_mouse_down = []
        self.just_mouse_up = []
        self.sfx = {}
        self.volume_music = self.__DEFAULT_VOLUME
        self.volume_effects = self.__DEFAULT_VOLUME
        self.winner = None
        self.fullscreen = False

        self.__frame_count = 0
        self.__perf_start = time.perf_counter_ns()
        self.__perf_stop = time.perf_counter_ns()
        self.__perf_index = 0
        self.__perf_results = [0] * 640
        self.__perf_surface = pygame.Surface((640, 360))

        if settings.DEBUG:
            self.__test_performance()

        # load settings from config file
        self.config = configparser.ConfigParser()
        self.__load_settings()

        # joystick support
        self.joysticks = [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]
        print("self.joysticks=", self.joysticks)

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
        # check if browser or desktop
        if settings.WASM:
            # browser
            self.screen: pygame.Surface = pygame.display.set_mode(
                settings.RESOLUTION
            )
        else:
            # desktop
            if self.fullscreen:
                self.screen: pygame.Surface = pygame.display.set_mode(
                    settings.RESOLUTION, pygame.FULLSCREEN | pygame.SCALED
                )
            else:
                self.screen: pygame.Surface = pygame.display.set_mode(
                    settings.RESOLUTION, pygame.SCALED
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

        # create the surface for our performance counter
        self.__perf_surface = pygame.Surface((640,360), pygame.SRCALPHA, 32).convert_alpha()

    # pygbag requires this be async to run the game
    async def run(self):
        self.debug_scene = scenes.Debug(self)

        while not self.quit:


            # process scene change requests (if any)
            self.__change_scenes()

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
            self.__perf_stop = time.perf_counter_ns()

            self.frame_time_ns = (self.__perf_stop - self.__perf_start)
            self.frame_time_ms = self.frame_time_ns / 1000000

            self.frame_load = self.frame_time_ms / (1000 / settings.FPS) * 100

            self.__perf_results[self.__perf_index] = self.frame_load

            # print performance data
            if settings.DEBUG:

                # use the debug scene's make_text method for us to render the performance data to a surfrace we can blit to the screen
                self.frame_report = self.debug_scene.make_text(
                    text="Frame Time: " + str(round(self.frame_time_ms, 1)) + "    Frame Load: " + str(round(self.frame_load, 1)) + " %",
                    color=(255,255,255),
                    font="assets/fonts/"+settings.FONT_SMALL,
                    fontSize=5,
                    stroke=True,
                    strokeColor=(0,0,0),
                    strokeThickness=1
                )

                # blit the performance data to the screen
                self.screen.blit(self.frame_report, (0, 0))

                # draw a clear vertical line on the performance surface to clear any prior result
                pygame.draw.line(self.__perf_surface, (0,0,0,0), (self.__perf_index, 0), (self.__perf_index, 360), 1)

                # draw a translucent red vertical line on the performance surface to represent 1% of frame load per pixel
                pygame.draw.line(self.__perf_surface, (255,0,0,50), (self.__perf_index, 360), (self.__perf_index, 360-self.__perf_results[self.__perf_index]), 1)

                # blit the performance surface to the screen
                self.screen.blit(self.__perf_surface, (0, 0))

            # increment the performance index
            self.__perf_index = (self.__perf_index + 1) % len(self.__perf_results)


            pygame.display.flip()
            self.__frame_count += 1

            # pygbag requires this to run the game
            await asyncio.sleep(0)

            # limit the game to 60 fps
            self.clock.tick(settings.FPS)

            # update the performance timer
            self.__perf_start = time.perf_counter_ns()

        # quit the game
        self.__quit()

    def __test_performance(self):
        results = []
        # set the performance timer to the current time high resolution
        best_test = 1e9
        worst_test = 0

        for j in range(200):
            self.__perf_start = time.perf_counter_ns()
            self.__perf_stop = time.perf_counter_ns()
            # print("perf_test: " + str(j) + " " + str(self.__perf_stop - self.__perf_start) + " ns")
            result = self.__perf_stop - self.__perf_start
            results.append(result)
            best_test = min(best_test, result)
            worst_test = max(worst_test, result)


        print("best result: " + str(best_test) + " ns")
        print("worst result: " + str(worst_test) + " ns")
        print("average result: " + str(sum(results) / len(results)) + " ns")
        print("raw results: " + str(results) + " ns")

    def get_events_and_input(self):
        # get input
        self.pressed = pygame.key.get_pressed()
        self.just_pressed = []
        self.just_released = []
        self.just_mouse_down = []
        self.just_mouse_up = []

        # get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                self.just_pressed.append(event.key)
            elif event.type == pygame.KEYUP:
                self.just_released.append(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.just_mouse_down.append(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.just_mouse_up.append(event.button)

        # check if ctrl and backquote was pressed to instantly quit the game
        if pygame.K_BACKQUOTE in self.just_pressed and (self.pressed[pygame.K_LCTRL] or self.pressed[pygame.K_RCTRL]):
            self.quit = True

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

    def __change_scenes(self):
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

    # return type is Scene
    def load_scene(self, scene: str) -> Scene:

        # while we are in here let's clean out the garbage
        # collect any old references to scenes that are no longer in the stack
        # this will help the garbage collector clean up any old scenes that are
        # no longer in use

        # check if self.jw exists in the stack
        if self.jw is not None:
            if self.jw not in self.scene:
                print("purging old jw reference")
                self.jw = None


        print("load_scene: " + scene)

        # check if the string passed in matches the name of a class in the scenes module
        if scene in dir(scenes):
            new_scene = eval("scenes." + scene + "(self)")
            if scene == "JackWizards":
                self.jw = new_scene
            return new_scene
        else:
            print("WARNING: Invalid scene name! Loading start scene!")
            return eval("scenes." + settings.SCENE_START + "(self)")

    def __load_settings(self):

        # set default settings
        self.fullscreen = False
        self.volume_effects = self.__DEFAULT_VOLUME
        self.volume_music = self.__DEFAULT_VOLUME

        # load settings from config file
        self.config.read("assets/config.ini")
        # check if the main section exists
        if "main" in self.config:
            # check if the fullscreen setting exists
            if "fullscreen" in self.config["main"]:
                self.fullscreen = self.config["main"].getboolean("fullscreen")

            # check if the volume settings exist and load them
            if "volume_music" in self.config["main"]:
                self.volume_music = int(self.config["main"]["volume_music"])

            if "volume_effects" in self.config["main"]:
                self.volume_effects = int(self.config["main"]["volume_effects"])



    def __save_settings(self):
        print("__save_settings")

        # check if the main section exists
        if "main" not in self.config:
            self.config["main"] = {}


        # save settings to config file
        self.config["main"]["volume_music"] = str(self.volume_music)
        self.config["main"]["volume_effects"] = str(self.volume_effects)
        self.config["main"]["fullscreen"] = str(self.fullscreen)


        with open("assets/config.ini", "w") as config_file:
            self.config.write(config_file)

    def frame_count(self):
        return self.__frame_count

    def __quit(self):

        # quit the game
        print("__quit")

        # save settings
        self.__save_settings()

        print("shutting down...")
        pygame.quit()
        sys.exit()