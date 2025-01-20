import pygame
from scene import Scene
from utils import *
import settings


class Console(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.slide_in_frames = 10
        self.slide_in_remaining = self.slide_in_frames
        self.terminal_output_cache = self.make_transparent_surface(
            self.screen.get_size()
        )
        self.terminal_surface = self.make_transparent_surface(self.screen.get_size())
        self.history = []
        self.command_history = []
        self.command = ""
        self.active = False
        self.last_render = None
        self.terminal_rows = 18
        self.terminal_row_height = 17
        self.standard_font_size = 16
        self.standard_stroke = 0
        self.standard_font = "assets/fonts/novem___.ttf"
        self.standard_color = (255, 255, 255)
        self.console_title = self.standard_text("PyGame Console")
        self.help_docs = [
            ">>HELP:",
            "This is a simple console. It will execute the given",
            "python unless provided an exact command as follows:",
            ">>HELP>>COMMAND LIST:",
            "clear         clear the console",
            "debug         toggle debug mode",
            "exit | quit   quit the game",
            "help | ?      show this help",
            'scene         use "scene" to commands',
            ">>HELP>>SCENE COMMANDS:",
            "scene len     show the number of scenes in the scene stack",
            "scene list    list the scenes in the scene stack",
            "scene init    call the __init__ method of scene beneath the console",
        ]

    def update(self):

        self.command += self.game.unicode

        for k in self.game.just_pressed:

            # delete the last character in the command
            if k == pygame.K_BACKSPACE:
                # check if a modifier is being held

                # capture the list of modifiers being held down
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                alt = pygame.key.get_mods() & pygame.KMOD_ALT
                super = pygame.key.get_mods() & pygame.KMOD_GUI

                if ctrl or alt or super:
                    # split the command into words
                    words = self.command.split(" ")

                    # rejoin the words without the last one
                    self.command = " ".join(words[:-1])
                else:
                    self.command = self.command[:-1]
                continue

            if k == pygame.K_DOWN:
                if len(self.command_history) == 0:
                    continue
                if self.history_pointer is None:
                    continue
                self.history_pointer += 1
                if self.history_pointer >= len(self.command_history):
                    self.history_pointer = len(self.command_history) - 1
                self.command = self.command_history[self.history_pointer]
                continue

            if k == pygame.K_UP:
                if len(self.command_history) == 0:
                    continue
                if self.history_pointer is None:
                    self.history_pointer = len(self.command_history) - 1
                else:
                    self.history_pointer -= 1

                if self.history_pointer < 0:
                    self.history_pointer = 0
                self.command = self.command_history[self.history_pointer]
                continue

            # execute the command in the console
            if k == pygame.K_RETURN:
                self.history_pointer = None
                self.history.append(self.command)
                # if this command already exists in the history, remove it so we can add it to the end
                if self.command in self.command_history:
                    self.command_history.remove(self.command)
                self.command_history.append(self.command)

                # make the basic
                #  case insensitive
                command_lower = self.command.lower()
                if command_lower == "exit" or command_lower == "quit":
                    self.log("Quitting the game.")
                    self.game.quit = True
                elif command_lower == "clear":
                    self.history = []
                elif command_lower == "help" or command_lower == "?":
                    self.history.extend(self.help_docs)
                    if len(self.game.scene) > 1:
                        # check for commands registered to the scene below this one
                        cmds = self.game.scene[-2].commands
                        if len(cmds) > 0:
                            self.history.append(">>HELP>>SCENE COMMANDS:")
                            # get the key and value of each command in the scene
                            for key, value in cmds.items():
                                self.history.append(key)

                elif command_lower == "debug":
                    settings.DEBUG = not settings.DEBUG
                elif command_lower == "scene len":
                    self.history.append(f">>Scene stack length: {len(self.game.scene)}")
                elif command_lower == "scene list":
                    for i, s in enumerate(self.game.scene):
                        self.history.append(f">>Scene {i}: {s.__class__.__name__}")
                elif command_lower == "scene init":
                    if len(self.game.scene) > 1:
                        self.game.scene[-2].__init__(self.game)

                # CUSTOM PYTHON EXECUTION AND CALLBACKS: POTENTIAL DANGER
                else:
                    # todo: add an option to check any running scene for a list of
                    #  available commands to be called back to from the console
                    # allowing scenes to hook custom functionality from the console
                    # - initial desire for this is to allow the map editor a simple
                    # command that when ran and supplied with a string after it that
                    # it would then use that string as a path to load and save from
                    # instead of the default. another command could be added to list the
                    # current working path for the map editor to see where it's current
                    # set to load and save from.

                    match_found = False
                    if len(self.game.scene) > 1:
                        # split the current command into words
                        words = self.command.split(" ")

                        # grab the first word and see if it is a registered command
                        command_word = words[0]

                        cmds = self.game.scene[-2].commands
                        if command_word in cmds:
                            # record that we found a match as to not attempt to
                            # execute this as python code
                            match_found = True

                            # make a string of the remaining words if the are any
                            # and pass that string to the callback function that
                            # has been registered for the command
                            if len(words) > 1:
                                cmds[command_word](" ".join(words[1:]))
                            else:
                                cmds[command_word]()

                    # we didn't match a command, so we'll try to execute the python
                    if not match_found:
                        try:
                            exec(self.command)
                        except Exception as e:
                            self.history.append(f">>Error: {e}")

                self.command = ""
                continue

    def draw(self):

        prompt_text = f"$ {self.command}"
        prompt_texture = self.standard_text(prompt_text)

        self.terminal_surface.fill((0, 0, 0, 200))

        self.terminal_surface.blit(self.console_title, (10, 10))
        self.terminal_surface.blit(prompt_texture, (10, 10 + self.terminal_row_height))

        # draw a blinking cursor next to the prompt texture
        if self.game.frame_count() % 60 < 30:
            cursor = self.standard_text("_")
            self.terminal_surface.blit(
                cursor, (10 + prompt_texture.get_width(), 10 + self.terminal_row_height)
            )

        # draw the most recent history elements
        drawn_cache = ""
        for dci in self.history[-self.terminal_rows :]:
            drawn_cache += str(dci) + "\n"

        if drawn_cache != self.last_render:
            self.last_render = drawn_cache

            # create a fresh surface to draw the terminal output
            self.terminal_output_cache = self.make_transparent_surface(
                self.screen.get_size()
            )
            for i, h in enumerate(self.history[-self.terminal_rows :]):
                self.terminal_output_cache.blit(
                    self.standard_text(str(h)),
                    (10, 19 + self.terminal_row_height * (i + 2)),
                )

        self.terminal_surface.blit(self.terminal_output_cache, (0, 0))

        if self.slide_in_remaining:
            self.slide_in_remaining -= 1
            self.screen.blit(
                self.terminal_surface,
                (
                    0,
                    -(
                        self.slide_in_remaining
                        / self.slide_in_frames
                        * settings.RESOLUTION[1]
                    ),
                ),
            )

        else:

            self.screen.blit(self.terminal_surface, (0, 0))
