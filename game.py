import os
import pygame
import settings
from scene import Scene
import scenes
import sys
import asyncio
import configparser
import time
from gamecontrollerdb import GameController


class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.mixer.init()
        pygame.joystick.init()

        self.debug_scene = None
        self.console = None

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
        self.qb_mode = None

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
        self.unicode = ""  # text input this frame

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
        self.__load_config()

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
            self.screen: pygame.Surface = pygame.display.set_mode(settings.RESOLUTION)
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
        self.scene_push_under = None

        # create the surface for our performance counter
        self.__perf_surface = pygame.Surface(
            (640, 360), pygame.SRCALPHA, 32
        ).convert_alpha()

    # pygbag requires this be async to run the game
    async def run(self):
        # create our debug and console scenes now so we can start logging
        self.debug_scene = scenes.Debug(self)
        self.console = scenes.Console(self)

        while not self.quit:

            # process scene change requests (if any)
            self.__change_scenes()

            # handle events and input
            self.get_events_and_input()

            # check if tilde was pressed to open the console
            if pygame.K_BACKQUOTE in self.just_pressed:
                self.__toggle_console()

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

            self.__update_performance_finish()

            pygame.display.flip()
            self.__frame_count += 1

            # pygbag requires this to run the game
            await asyncio.sleep(0)

            # limit the game to 60 fps
            self.clock.tick(settings.FPS)

            # start the performance update
            self.__update_performance_start()

        # quit the game
        self.__quit()

    def __update_performance_start(self):

        # update the performance timer
        self.__perf_start = time.perf_counter_ns()

    def __update_performance_finish(self):

        # update the display
        self.__perf_stop = time.perf_counter_ns()

        self.frame_time_ns = self.__perf_stop - self.__perf_start
        self.frame_time_ms = self.frame_time_ns / 1000000

        self.frame_load = self.frame_time_ms / (1000 / settings.FPS) * 100

        self.__perf_results[self.__perf_index] = self.frame_load

        # show performance data
        if settings.DEBUG:

            # use the debug scene's make_text method for us to render the performance data to a surfrace we can blit to the screen
            self.frame_report = self.debug_scene.make_text(
                text="Frame Time: "
                + str(round(self.frame_time_ms, 1))
                + "    Frame Load: "
                + str(round(self.frame_load, 1))
                + " %",
                color=(255, 255, 255),
                font="assets/fonts/" + settings.FONT_SMALL,
                fontSize=5,
                stroke=True,
                strokeColor=(0, 0, 0),
                strokeThickness=1,
            )

            # blit the performance data to the screen
            self.screen.blit(self.frame_report, (0, 0))

            # draw a clear vertical line on the performance surface to clear any prior result
            pygame.draw.line(
                self.__perf_surface,
                (0, 0, 0, 0),
                (self.__perf_index, 0),
                (self.__perf_index, 360),
                1,
            )

            # draw a translucent red vertical line on the performance surface to represent 1% of frame load per pixel
            pygame.draw.line(
                self.__perf_surface,
                (255, 0, 0, 50),
                (self.__perf_index, 360),
                (self.__perf_index, 360 - self.__perf_results[self.__perf_index]),
                1,
            )

            # blit the performance surface to the screen
            self.screen.blit(self.__perf_surface, (0, 0))

        # increment the performance index
        self.__perf_index = (self.__perf_index + 1) % len(self.__perf_results)

    def __test_performance(self):
        results = []
        # set the performance timer to the current time high resolution
        best_test = 1e9
        worst_test = 0

        for j in range(200):
            self.__perf_start = time.perf_counter_ns()
            self.__perf_stop = time.perf_counter_ns()
            # self.log("perf_test: " + str(j) + " " + str(self.__perf_stop - self.__perf_start) + " ns")
            result = self.__perf_stop - self.__perf_start
            results.append(result)
            best_test = min(best_test, result)
            worst_test = max(worst_test, result)

        self.log("best result: " + str(best_test) + " ns")
        self.log("worst result: " + str(worst_test) + " ns")
        self.log("average result: " + str(sum(results) / len(results)) + " ns")
        self.log("raw results: " + str(results) + " ns")

    def get_events_and_input(self):
        # get input
        self.unicode = ""
        self.pressed = pygame.key.get_pressed()
        self.just_pressed = []
        self.just_released = []
        self.just_mouse_down = []
        self.just_mouse_up = []

        # capture the list of modifiers being held down
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        alt = pygame.key.get_mods() & pygame.KMOD_ALT

        # get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                self.just_pressed.append(event.key)

                reject_unicode = False

                # attempt to append the unicode character to the unicode string
                # if it's not in the list of keys to reject or a modifier key

                # other than shift is being held
                keys_to_reject = [
                    pygame.K_RETURN,
                    pygame.K_TAB,
                    pygame.K_BACKSPACE,
                    pygame.K_BACKQUOTE,
                    pygame.K_ESCAPE,
                    pygame.K_LSHIFT,
                    pygame.K_RSHIFT,
                    pygame.K_LCTRL,
                    pygame.K_RCTRL,
                    pygame.K_LALT,
                    pygame.K_RALT,
                    pygame.K_CAPSLOCK,
                    pygame.K_NUMLOCK,
                    pygame.K_SCROLLLOCK,
                    pygame.K_INSERT,
                    pygame.K_DELETE,
                    pygame.K_HOME,
                    pygame.K_END,
                    pygame.K_PAGEUP,
                    pygame.K_PAGEDOWN,
                    pygame.K_UP,
                    pygame.K_DOWN,
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                    pygame.K_F1,
                    pygame.K_F2,
                    pygame.K_F3,
                    pygame.K_F4,
                    pygame.K_F5,
                    pygame.K_F6,
                    pygame.K_F7,
                    pygame.K_F8,
                    pygame.K_F9,
                    pygame.K_F10,
                    pygame.K_F11,
                    pygame.K_F12,
                    pygame.K_PRINTSCREEN,
                ]

                if event.key in keys_to_reject:
                    reject_unicode = True

                # check ctrl or alt are being held down
                if ctrl or alt:
                    reject_unicode = True

                if not reject_unicode:
                    try:
                        self.unicode += event.unicode
                    except:
                        pass

            elif event.type == pygame.KEYUP:
                self.just_released.append(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.just_mouse_down.append(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.just_mouse_up.append(event.button)

        # check if ctrl and backquote was pressed to instantly quit the game
        if pygame.K_BACKQUOTE in self.just_pressed and (
            self.pressed[pygame.K_LCTRL] or self.pressed[pygame.K_RCTRL]
        ):
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
        found: bool = scene in dir(scenes)
        if found:
            self.log(f"valid scene name: {scene}")
        else:
            self.log(f"Warning! Invalid scene name: {scene}")
        return found

    def __quit_all_scenes(self):
        # call all active scene's quit methods
        for scene in self.scene:
            try:
                scene.quit()
                self.log(f"ran scene's quit method: {scene.__class__.__name__}")
            except:
                self.log(
                    f"failed to run scene's quit method: {scene.__class__.__name__}"
                )

    def __change_scenes(self):
        # check for scene changes

        # start off by looking for a replacement scene to rebuild the stack
        if self.scene_replace is not None:

            if type(self.scene_replace) == str:
                self.log("scene_replace: " + self.scene_replace)
                if self.valid_scene_name(self.scene_replace):
                    self.__quit_all_scenes()

                    self.scene = []
                    self.scene.append(self.load_scene(self.scene_replace))

            if type(self.scene_replace) == list:
                self.log("scene_replace received a list of scenes to replace the stack")
                self.__quit_all_scenes()

                self.scene = []
                for scene in self.scene_replace:
                    self.log("scene_replace: " + scene)

                    if self.valid_scene_name(scene):
                        self.scene.append(self.load_scene(scene))
                    else:
                        self.log(
                            "scene_replace: " + scene + ", WARNING: Invalid scene name!"
                        )
            self.scene_replace = None

        # next, look for a pop request to clear the stack
        if self.scene_pop is not None:
            if len(self.scene) > 1:
                # if scene pop was given an integer, pop that many scenes
                # otherwise, pop only one scene
                if isinstance(self.scene_pop, int):
                    self.log("scene_pop: " + str(self.scene_pop))
                    if self.scene_pop >= len(self.scene):
                        self.log("WARNING: Cannot pop more scenes than exist! Exiting!")
                        self.__quit_all_scenes()
                        self.quit = True
                    else:
                        for _ in range(self.scene_pop):
                            # call the quit method of the scene being popped
                            try:
                                self.log(
                                    f"Running scene's quit method: {self.scene[-1].__class__.__name__}"
                                )
                                self.scene[-1].quit()
                            except:
                                self.log(
                                    f"Failed to run scene's quit method: {self.scene[-1].__class__.__name__}"
                                )
                            self.scene.pop()
                else:
                    self.log("scene_pop: 1")
                    self.scene.pop()
            else:
                self.log("WARNING: Cannot pop last scene! Exiting!")
                self.__quit_all_scenes()
                self.quit = True
            self.scene_pop = None

        if self.scene_push is not None:
            # if scene push is a string, push that scene onto the stack
            if type(self.scene_push) == str:

                if self.valid_scene_name(self.scene_push):
                    self.log("scene_push: " + self.scene_push)
                    self.scene.append(self.load_scene(self.scene_push))
                else:
                    self.log(
                        "scene_push: "
                        + self.scene_push
                        + ", WARNING: Invalid scene name!"
                    )

            if type(self.scene_push) == list:
                self.log("scene_push received a list of scenes to push onto the stack")
                # if scene push is a list, push each scene onto the stack
                for scene in self.scene_push:
                    if self.valid_scene_name(scene):
                        self.log("scene_push: " + scene)
                        self.scene.append(self.load_scene(scene))
                    else:
                        self.log(
                            "scene_push: " + scene + ", WARNING: Invalid scene name!"
                        )
            self.scene_push = None

        if self.scene_push_under is not None:
            # if scene push is a string, push that scene onto the stack under the current scene
            if type(self.scene_push_under) == str:

                if self.valid_scene_name(self.scene_push_under):
                    self.log("scene_push_under: " + self.scene_push_under)
                    self.scene.insert(-1, self.load_scene(self.scene_push_under))
                else:
                    self.log(
                        "scene_push_under: "
                        + self.scene_push_under
                        + ", WARNING: Invalid scene name!"
                    )

            if type(self.scene_push_under) == list:
                self.log(
                    "scene_push_under received a list of scenes to push onto the stack"
                )
                # if scene push is a list, push each scene onto the stack under the current scene
                for scene in self.scene_push_under:
                    if self.valid_scene_name(scene):
                        self.log("scene_push_under: " + scene)
                        self.scene.insert(-1, self.load_scene(scene))
                    else:
                        self.log(
                            "scene_push_under: "
                            + scene
                            + ", WARNING: Invalid scene name!"
                        )
            self.scene_push_under = None

    # return type is Scene
    def load_scene(self, scene: str) -> Scene:

        self.log("load_scene: " + scene)

        # while we are in here let's clean out the garbage
        # collect any old references to scenes that are no longer in the stack
        # this will help the garbage collector clean up any old scenes that are
        # no longer in use

        # check if self.jw exists in the stack
        if self.jw is not None:
            if self.jw not in self.scene:
                self.log("purging old jw reference")
                self.jw = None

        # check if the string passed in matches the name of a class in the scenes module
        if self.valid_scene_name(scene):
            # create our new scene
            new_scene = eval("scenes." + scene + "(self)")

            # store a reference the jackwizards game scene for easy access
            if scene == "JackWizards":
                self.jw = new_scene

            return new_scene
        else:
            self.log("WARNING: Invalid scene name! Loading start scene!")
            return eval("scenes." + settings.SCENE_START + "(self)")

    def get_scene_by_name(self, scene: str) -> Scene:

        result = None
        for s in self.scene:
            if s.__class__.__name__ == scene:
                result = s
                break

        if result is None:
            self.log("WARNING: get_scene_by_name failed to find scene: " + scene)
        else:
            self.log("get_scene_by_name found scene: " + scene)
        return result

    def __load_config(self):

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

    def __save_config(self):
        self.log("__save_config called")

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

    def __toggle_console(self):
        # toggle the console
        self.console.active = not self.console.active

        if self.console.active:
            # if it is now active add it to the scene stack
            self.just_pressed.remove(pygame.K_BACKQUOTE)
            self.scene.append(self.console)
        else:
            # if it is now inactive remove it from the scene stack
            self.scene_pop = 1
            self.__change_scenes()

    def __quit(self):

        # quit the game
        self.log("__quit")

        # save settings
        self.__save_config()

        self.__quit_all_scenes()

        self.log("shutting down...")
        pygame.quit()
        sys.exit()

    def log(self, message: str):
        if self.console is not None:
            self.console.history.append(message)
        print(f">> {message}")
