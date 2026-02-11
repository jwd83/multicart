import os
import pygame
import settings
from scene import Scene
import scenes
import sys
import asyncio
import configparser
import time
from gamecontrollerdb import GameController, mappings_by_guid


class InputAction:
    """Represents the state of a single input action (e.g., 'jump')."""

    def __init__(self):
        self.pressed = False  # Currently held down
        self.just_pressed = False  # Pressed this frame
        self.just_released = False  # Released this frame
        self.axis = 0.0  # For analog values (-1.0 to 1.0)


class Game:
    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        pygame.joystick.init()

        # Initialize controllers
        self.controllers = []
        self._init_controllers()

        # Initialize unified input system
        self.input = {}
        self._init_input_actions()

        self.debug_scene = None
        self.console = None

        # hardcode some default values

        self.WIDTH = settings.RESOLUTION[0]
        self.HEIGHT = settings.RESOLUTION[1]

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
            if (
                sound.endswith(".wav")
                or sound.endswith(".ogg")
                or sound.endswith(".mp3")
            ):
                sound_name = sound.split(".")[0]
                self.sfx[sound_name] = pygame.mixer.Sound("assets/sounds/" + sound)

        # create a window
        # check if browser or desktop
        if settings.WASM:
            # browser
            self.screen: pygame.Surface = pygame.display.set_mode(settings.RESOLUTION)
        else:
            # desktop
            self.log(f"Running on desktop: {os.name}")

            # check if we are on windows and disable windows scaling
            if os.name == "nt":
                # disable windows scaling
                import ctypes

                ctypes.windll.user32.SetProcessDPIAware()

                # TODO:     from stackoverflow this might also be needed
                # https://gamedev.stackexchange.com/questions/105750/pygame-fullsreen-display-issue

                # Calling ctypes.windll.user32.SetProcessDPIAware() will disable
                # the screen stretching. The reason true_res = (windll.user32.GetSystemMetrics(0),windll.user32.GetSystemMetrics(1))
                # needs to be called and used for the resolution is because there is fullscreen issues
                # when using a resolution that is not native. If one is using a resolution smaller than
                # this, they can simply create a surface for the game to run on and keep the sides black,
                # or he/she can stretch this surface to fit the display size.

                # true_res = (windll.user32.GetSystemMetrics(0),windll.user32.GetSystemMetrics(1))
                # pygame.display.set_mode(true_res,pygame.Fullscreen)

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

            # if mouse_lock then we hide and set grab true
            # else if mouse_hide then we hide and set grab false
            # else we show and set grab false

            # check the mouse_lock property of the top scene.
            # If it is true, lock the mouse to the window if we
            # have focus

            # check if the current scene is using mouse lock
            if self.scene[-1].mouse_lock:
                if pygame.mouse.get_focused():
                    if pygame.mouse.get_visible():
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                else:
                    if not pygame.mouse.get_visible():
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
            else:
                # the current scene was NOT using mouse lock, check if it's using mouse hide
                if self.scene[-1].mouse_hide:

                    # the current scene is using mouse hide, hide the mouse if it's visible
                    if pygame.mouse.get_visible():
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(False)
                else:
                    # the current scene is not using mouse lock or hide, show the mouse if it's hidden
                    if not pygame.mouse.get_visible():
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
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
                if event.mod & (pygame.KMOD_CTRL | pygame.KMOD_ALT):
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
            elif event.type == pygame.JOYDEVICEADDED:
                print("Controller connected!")
                self._init_controllers()
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("Controller disconnected!")
                self._init_controllers()

        # get key state AFTER processing events so pressed[] is in sync
        self.pressed = pygame.key.get_pressed()

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

        # Update all connected controllers
        for controller in self.controllers:
            controller.update()

        # Merge keyboard + controller into unified input
        self._update_unified_input()

    def _init_controllers(self):
        """Detect and initialize any connected game controllers."""
        # Default Xbox-style mapping for controllers not in the database
        DEFAULT_XBOX_MAPPINGS = [
            "a:b0", "b:b1", "x:b2", "y:b3",
            "leftshoulder:b4", "rightshoulder:b5",
            "back:b6", "start:b7",
            "leftstick:b8", "rightstick:b9",
            "leftx:a0", "lefty:a1",
            "rightx:a2", "righty:a3",
            "lefttrigger:a4", "righttrigger:a5",
            "dpup:h0.1", "dpdown:h0.4", "dpleft:h0.8", "dpright:h0.2",
        ]

        self.controllers = []
        joystick_count = pygame.joystick.get_count()

        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            guid = joystick.get_guid()
            mappings = mappings_by_guid(guid)

            if not mappings:
                # Use default Xbox mapping as fallback
                mappings = DEFAULT_XBOX_MAPPINGS
                print(f"Using default Xbox mapping for: {joystick.get_name()}")

            controller = GameController(joystick, mappings)
            self.controllers.append(controller)
            print(f"Controller ready: {joystick.get_name()}")

    def _init_input_actions(self):
        """Initialize all input action slots."""
        actions = [
            "left",
            "right",
            "up",
            "down",
            "jump",
            "dash",
            "throw",
            "menu",
            "confirm",
            "cancel",
            "inventory",
        ]
        for action in actions:
            self.input[action] = InputAction()

    def _update_unified_input(self):
        """Merge keyboard and controller input into unified input dict."""
        STICK_DEADZONE = 0.3

        # Get primary controller (if any)
        ctrl = self.controllers[0] if self.controllers else None

        # Helper to update an action's state
        def update_action(action_name, kb_pressed, kb_just_pressed, ctrl_pressed, ctrl_just_pressed):
            action = self.input[action_name]
            new_pressed = kb_pressed or ctrl_pressed
            new_just_pressed = kb_just_pressed or ctrl_just_pressed

            # Track just_released transition
            if not new_pressed and action.pressed:
                action.just_released = True
            else:
                action.just_released = False

            # Track just_pressed
            if new_just_pressed or (new_pressed and not action.pressed):
                action.just_pressed = True
            else:
                action.just_pressed = False

            action.pressed = new_pressed

        # Movement - Left
        kb_left_pressed = self.pressed[pygame.K_LEFT] or self.pressed[pygame.K_a]
        kb_left_just = pygame.K_LEFT in self.just_pressed or pygame.K_a in self.just_pressed
        ctrl_left_pressed = False
        ctrl_left_just = False
        if ctrl:
            ctrl_left_pressed = "left" in ctrl.held or ctrl.l_thumb[0] < -STICK_DEADZONE
            ctrl_left_just = "left" in ctrl.pressed
        update_action("left", kb_left_pressed, kb_left_just, ctrl_left_pressed, ctrl_left_just)
        self.input["left"].axis = ctrl.l_thumb[0] if ctrl and ctrl.l_thumb[0] < -STICK_DEADZONE else (-1.0 if kb_left_pressed else 0.0)

        # Movement - Right
        kb_right_pressed = self.pressed[pygame.K_RIGHT] or self.pressed[pygame.K_d]
        kb_right_just = pygame.K_RIGHT in self.just_pressed or pygame.K_d in self.just_pressed
        ctrl_right_pressed = False
        ctrl_right_just = False
        if ctrl:
            ctrl_right_pressed = "right" in ctrl.held or ctrl.l_thumb[0] > STICK_DEADZONE
            ctrl_right_just = "right" in ctrl.pressed
        update_action("right", kb_right_pressed, kb_right_just, ctrl_right_pressed, ctrl_right_just)
        self.input["right"].axis = ctrl.l_thumb[0] if ctrl and ctrl.l_thumb[0] > STICK_DEADZONE else (1.0 if kb_right_pressed else 0.0)

        # Movement - Up
        kb_up_pressed = self.pressed[pygame.K_UP] or self.pressed[pygame.K_w]
        kb_up_just = pygame.K_UP in self.just_pressed or pygame.K_w in self.just_pressed
        ctrl_up_pressed = False
        ctrl_up_just = False
        if ctrl:
            ctrl_up_pressed = "up" in ctrl.held or ctrl.l_thumb[1] < -STICK_DEADZONE
            ctrl_up_just = "up" in ctrl.pressed
        update_action("up", kb_up_pressed, kb_up_just, ctrl_up_pressed, ctrl_up_just)

        # Movement - Down
        kb_down_pressed = self.pressed[pygame.K_DOWN] or self.pressed[pygame.K_s]
        kb_down_just = pygame.K_DOWN in self.just_pressed or pygame.K_s in self.just_pressed
        ctrl_down_pressed = False
        ctrl_down_just = False
        if ctrl:
            ctrl_down_pressed = "down" in ctrl.held or ctrl.l_thumb[1] > STICK_DEADZONE
            ctrl_down_just = "down" in ctrl.pressed
        update_action("down", kb_down_pressed, kb_down_just, ctrl_down_pressed, ctrl_down_just)

        # Jump - Space/W/Up + Controller A
        kb_jump_pressed = self.pressed[pygame.K_SPACE]
        kb_jump_just = pygame.K_SPACE in self.just_pressed
        ctrl_jump_pressed = ctrl and "a" in ctrl.held
        ctrl_jump_just = ctrl and "a" in ctrl.pressed
        update_action("jump", kb_jump_pressed, kb_jump_just, ctrl_jump_pressed, ctrl_jump_just)

        # Dash - X key + Controller X
        kb_dash_pressed = self.pressed[pygame.K_x]
        kb_dash_just = pygame.K_x in self.just_pressed
        ctrl_dash_pressed = ctrl and "x" in ctrl.held
        ctrl_dash_just = ctrl and "x" in ctrl.pressed
        update_action("dash", kb_dash_pressed, kb_dash_just, ctrl_dash_pressed, ctrl_dash_just)

        # Throw - Z key (held) + Controller Y (held)
        kb_throw_pressed = self.pressed[pygame.K_z]
        kb_throw_just = pygame.K_z in self.just_pressed
        ctrl_throw_pressed = ctrl and "y" in ctrl.held
        ctrl_throw_just = ctrl and "y" in ctrl.pressed
        update_action("throw", kb_throw_pressed, kb_throw_just, ctrl_throw_pressed, ctrl_throw_just)

        # Menu - Escape + Controller Start
        kb_menu_pressed = self.pressed[pygame.K_ESCAPE]
        kb_menu_just = pygame.K_ESCAPE in self.just_pressed
        ctrl_menu_pressed = ctrl and "start" in ctrl.held
        ctrl_menu_just = ctrl and "start" in ctrl.pressed
        update_action("menu", kb_menu_pressed, kb_menu_just, ctrl_menu_pressed, ctrl_menu_just)

        # Inventory - I key + Controller Select/Back
        kb_inv_pressed = self.pressed[pygame.K_i]
        kb_inv_just = pygame.K_i in self.just_pressed
        ctrl_inv_pressed = ctrl and "select" in ctrl.held
        ctrl_inv_just = ctrl and "select" in ctrl.pressed
        update_action("inventory", kb_inv_pressed, kb_inv_just, ctrl_inv_pressed, ctrl_inv_just)

        # Confirm - Enter/Space + Controller A
        kb_confirm_pressed = self.pressed[pygame.K_RETURN] or self.pressed[pygame.K_SPACE]
        kb_confirm_just = pygame.K_RETURN in self.just_pressed or pygame.K_SPACE in self.just_pressed
        ctrl_confirm_pressed = ctrl and "a" in ctrl.held
        ctrl_confirm_just = ctrl and "a" in ctrl.pressed
        update_action("confirm", kb_confirm_pressed, kb_confirm_just, ctrl_confirm_pressed, ctrl_confirm_just)

        # Cancel - Escape + Controller B
        kb_cancel_pressed = self.pressed[pygame.K_ESCAPE]
        kb_cancel_just = pygame.K_ESCAPE in self.just_pressed
        ctrl_cancel_pressed = ctrl and "b" in ctrl.held
        ctrl_cancel_just = ctrl and "b" in ctrl.pressed
        update_action("cancel", kb_cancel_pressed, kb_cancel_just, ctrl_cancel_pressed, ctrl_cancel_just)

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
        self.console.slide_in_remaining = self.console.slide_in_frames

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
