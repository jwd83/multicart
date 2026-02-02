import sys
import pygame


class GameController:
    def __init__(self, joystick, mappings, verbose=False):

        self.reset()
        self.verbose = verbose

        if self.verbose:
            print(f"Hats on Joystick: {joystick.get_numhats()}")

        self.joystick = joystick
        self.instance_id = joystick.get_instance_id()
        self.mappings = mappings

        self.dpad_is_hat = True
        self.build_lookups()

    def extract_lookup(self, lookup):
        for k in self.mappings:
            if k.startswith(lookup + ":"):
                # return the value of the mapping after the colon
                return k.split(":")[1]

    def build_lookups(self):
        # build the lookups
        self.lookups["a"] = int(self.extract_lookup("a")[1:])
        self.lookups["b"] = int(self.extract_lookup("b")[1:])
        self.lookups["x"] = int(self.extract_lookup("x")[1:])
        self.lookups["y"] = int(self.extract_lookup("y")[1:])
        self.lookups["r1"] = int(self.extract_lookup("rightshoulder")[1:])
        self.lookups["l1"] = int(self.extract_lookup("leftshoulder")[1:])
        self.lookups["r2"] = int(self.extract_lookup("righttrigger")[1:])
        self.lookups["l2"] = int(self.extract_lookup("lefttrigger")[1:])
        self.lookups["l3"] = int(self.extract_lookup("leftstick")[1:])
        self.lookups["r3"] = int(self.extract_lookup("rightstick")[1:])
        self.lookups["select"] = int(self.extract_lookup("back")[1:])
        self.lookups["start"] = int(self.extract_lookup("start")[1:])
        self.lookups["lx"] = int(self.extract_lookup("leftx")[1:])
        self.lookups["ly"] = int(self.extract_lookup("lefty")[1:])
        self.lookups["rx"] = int(self.extract_lookup("rightx")[1:])
        self.lookups["ry"] = int(self.extract_lookup("righty")[1:])

        # on some controllers dpad is buttons but on most it is a hat
        # let's check dpad up to see if it's referencing a hat (h) or button (b)
        dpup = str(self.extract_lookup("dpup"))
        if str(dpup).startswith("h"):
            self.dpad_is_hat = True

            # grab the hat number in the character after the h
            hat_num = int(dpup[1:2])

            self.lookups["up"] = hat_num
            self.lookups["down"] = hat_num
            self.lookups["left"] = hat_num
            self.lookups["right"] = hat_num

        else:
            # bind the dpad to the buttons
            self.dpad_is_hat = False

            self.lookups["up"] = int(self.extract_lookup("dpup")[1:])
            self.lookups["down"] = int(self.extract_lookup("dpdown")[1:])
            self.lookups["left"] = int(self.extract_lookup("dpleft")[1:])
            self.lookups["right"] = int(self.extract_lookup("dpright")[1:])

    def reset(self):
        self.held = []
        self.pressed = []
        self.released = []
        self.l_trigger = 0.0
        self.r_trigger = 0.0
        self.l_thumb = (0.0, 0.0)
        self.r_thumb = (0.0, 0.0)
        self.hats = []

        self.__events_to_handle = [
            pygame.JOYAXISMOTION,
            pygame.JOYBALLMOTION,
            pygame.JOYHATMOTION,
            pygame.JOYBUTTONDOWN,
            pygame.JOYBUTTONUP,
        ]

        self.lookups = {
            "a": None,
            "b": None,
            "x": None,
            "y": None,
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "l1": None,
            "r1": None,
            "l3": None,
            "r3": None,
            "select": None,
            "start": None,
            "l_thumb": None,
            "r_thumb": None,
            "zl": None,
            "zr": None,
        }

    def handle_events(self, event: pygame.event.Event):

        # we only care about events that are related to the joystick
        if event.type not in self.__events_to_handle:
            return

        # we only care about events that are related to this joystick
        if event.instance_id != self.instance_id:
            return

    # logic for handling a generic hat input each frame
    def __update_hat_input(self, button):

        hat_pressed = False

        # check if the button is mapped
        if self.lookups[button] is not None:

            # get the data from the hat
            x, y = self.hats[self.lookups[button]]

            #  print(f"Button: {button}, x: {x}, y: {y}")

            if button == "up" and y == 1:
                hat_pressed = True

            # check if the hat is pressed in the direction of the button
            if button == "down" and y == -1:
                hat_pressed = True

            if button == "left" and x == -1:
                hat_pressed = True

            if button == "right" and x == 1:
                hat_pressed = True

            # check if the button is pressed
            if hat_pressed:
                # the button was pressed so ...

                # check if the button is already pressed

                if button in self.held:
                    # the button was already pressed
                    # make sure it's not in the pressed list
                    # any longer
                    if button in self.pressed:
                        self.pressed.remove(button)

                else:
                    # the button was just pressed
                    self.pressed.append(button)
                    self.held.append(button)
            else:
                # check if the button was previously pressed
                if button in self.held:
                    # the button was previously pressed
                    # so it is now released
                    self.held.remove(button)
                    if button in self.pressed:
                        self.pressed.remove(button)
                    self.released.append(button)
                else:
                    # the button was not previously held and still is not
                    # make sure it's not in the released list any longer
                    if button in self.released:
                        self.released.remove(button)

    # logic for handling a generic button input each frame
    def __update_button_input(self, button):

        # check if the button is mapped
        if self.lookups[button] is not None:

            # check if the button is pressed
            if self.joystick.get_button(self.lookups[button]):
                # the button was pressed so ...

                # check if the button is already pressed

                if button in self.held:
                    # the button was already pressed
                    # make sure it's not in the pressed list
                    # any longer
                    if button in self.pressed:
                        self.pressed.remove(button)

                else:
                    # the button was just pressed
                    self.pressed.append(button)
                    self.held.append(button)
            else:
                # check if the button was previously pressed
                if button in self.held:
                    # the button was previously pressed
                    # so it is now released
                    self.held.remove(button)
                    if button in self.pressed:
                        self.pressed.remove(button)
                    self.released.append(button)
                else:
                    # the button was not previously held and still is not
                    # make sure it's not in the released list any longer
                    if button in self.released:
                        self.released.remove(button)

    # to be called once per frame
    def update(self):

        # update the list of hats
        self.hats = [
            self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())
        ]

        self.__update_button_input("a")
        self.__update_button_input("b")
        self.__update_button_input("x")
        self.__update_button_input("y")
        self.__update_button_input("l1")
        self.__update_button_input("r1")
        self.__update_button_input("l3")
        self.__update_button_input("r3")
        self.__update_button_input("select")
        self.__update_button_input("start")

        # update sticks and triggers
        self.l_thumb = (
            self.joystick.get_axis(self.lookups["lx"]),
            self.joystick.get_axis(self.lookups["ly"]),
        )
        self.r_thumb = (
            self.joystick.get_axis(self.lookups["rx"]),
            self.joystick.get_axis(self.lookups["ry"]),
        )
        self.l_trigger = self.joystick.get_axis(self.lookups["l2"])
        self.r_trigger = self.joystick.get_axis(self.lookups["r2"])

        # check if the dpad is buttons or a hat
        if not self.dpad_is_hat:
            # perform button update of dpad
            self.__update_button_input("up")
            self.__update_button_input("down")
            self.__update_button_input("left")
            self.__update_button_input("right")

        else:
            # perform hat update of dpad
            self.__update_hat_input("up")
            self.__update_hat_input("down")
            self.__update_hat_input("left")
            self.__update_hat_input("right")


# returns the string representation of the platform the script is running on
# in the format expected by the gamecontrollerdb.txt file. Returns 'unknown' if
# the platform is not recognized.
def parse_file(field, value):

    platform = get_platform()

    lines = None

    # load the gamecontrollerdb.txt file
    with open("gamecontrollerdb.txt", "r") as file:
        lines = file.readlines()

    # iterate through the lines of the file
    if lines is None:
        return None

    for line in lines:

        # skip comments
        if line.startswith("#"):
            continue

        # skip any blank lines
        if line.strip() == "":
            continue

        # split the line into fields
        fields = line.split(",")
        fields_count = len(fields)

        # make sure it has at least 4 fields, the minimum required
        # for there to be at least a guid, name, a single mapping and platform.
        # there is also an extra comma at the end of the line, so we need to
        # account for that
        if fields_count < 5:
            continue

        l_guid = fields[0].strip()
        l_name = fields[1].strip()
        l_mappings = fields[2:-2]
        l_platform = fields[-2].strip()

        # check if the platform matches
        if l_platform.endswith(platform) == False:
            continue

        # check if we are looking for a guid or a name
        match_found = False
        if field == "guid":
            if l_guid == value:
                match_found = True

        elif field == "name":
            if l_name == value:
                match_found = True

        # if we found a match, return the mappings
        if match_found:
            return l_mappings

        # print(f"Processing line. Fields count: {fields_count}, guid: {l_guid}, name: {l_name}, mappings: {l_mappings}, platform: {l_platform}")
        # sys.exit(0)
    return None


def mappings_by_name(name):
    return parse_file("name", name)


def mappings_by_guid(guid):
    return parse_file("guid", guid)


def get_platform():

    platform = sys.platform

    if platform.startswith("win32"):
        return "Windows"
    elif platform.startswith("darwin"):
        return "Mac OS X"
    elif platform.startswith("linux"):
        return "Linux"
    else:
        # default to windows if we can't determine the platform
        return "unknown"


if __name__ == "__main__":
    print("Running tests on : " + get_platform())

    # #
    # print(mappings_by_guid('03000000c82d00000161000000010000'))
    # print(mappings_by_name('8BitDo SN30 Pro'))

    # start pygame
    pygame.init()

    pygame.joystick.init()
    joysticks = [
        pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
    ]

    font = pygame.font.Font(None, 36)
    print(f"Joysticks found: {len(joysticks)}")

    for joystick in joysticks:
        print(f"Joystick name: {joystick.get_name()}")
        print(f"Joystick guid: {joystick.get_guid()}")
        joy_map = mappings_by_guid(joystick.get_guid())
        print(f"Joystick mappings: {joy_map}")

        if joy_map is not None:
            game_controller = GameController(joystick, joy_map)
            print(f"Game controller created: {game_controller}")

            # make a window to draw to

            screen = pygame.display.set_mode((800, 600))
            clock = pygame.time.Clock()

            while True:
                # clear the screen
                screen.fill((0, 0, 0))

                # draw text on the screen for held, pressed, released

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)

                    # game_controller.handle_events(event)
                # fill the screen with black and draw it

                # update the game controller
                game_controller.update()

                x_positions = {
                    "a": 120,
                    "b": 140,
                    "x": 160,
                    "y": 180,
                    "l1": 200,
                    "r1": 230,
                    "up": 250,
                    "down": 250,
                    "left": 320,
                    "right": 320,
                    "l3": 400,
                    "r3": 440,
                    "select": 480,
                    "start": 560,
                }

                y_positions = {
                    "pressed": 0,
                    "held": 40,
                    "released": 80,
                    "left stick": 120,
                    "right stick": 160,
                    "left trigger": 200,
                    "right trigger": 240,
                }

                white = (255, 255, 255)
                blue = (0, 0, 255)
                green = (0, 255, 0)
                orange = (255, 165, 0)

                for k, v in y_positions.items():
                    text = font.render(k, True, white)
                    screen.blit(text, (0, v))

                # draw analog stick and trigger values
                text = font.render(f"{game_controller.l_thumb}", True, white)
                screen.blit(text, (200, y_positions["left stick"]))
                text = font.render(f"{game_controller.r_thumb}", True, white)
                screen.blit(text, (200, y_positions["right stick"]))
                text = font.render(f"{game_controller.l_trigger}", True, white)
                screen.blit(text, (200, y_positions["left trigger"]))
                text = font.render(f"{game_controller.r_trigger}", True, white)
                screen.blit(text, (200, y_positions["right trigger"]))

                for check in [
                    "a",
                    "b",
                    "x",
                    "y",
                    "up",
                    "down",
                    "left",
                    "right",
                    "r1",
                    "l1",
                    "l3",
                    "r3",
                    "select",
                    "start",
                ]:
                    if check in game_controller.pressed:
                        print(f"{check} button pressed")

                        # draw the letter on the screen
                        text = font.render(check, True, green)
                        screen.blit(text, (x_positions[check], y_positions["pressed"]))

                    if check in game_controller.held:
                        # this is a bit obnoxious on held in the terminal
                        # maybe think about checking in pressed and writing
                        # held there to let the user know it is now being
                        # held.
                        #
                        # print(f"{check} button held")

                        # draw the letter on the screen
                        text = font.render(check, True, blue)
                        screen.blit(text, (x_positions[check], y_positions["held"]))

                    if check in game_controller.released:
                        print(f"{check} button released")

                        # draw the letter on the screen
                        text = font.render(check, True, orange)
                        screen.blit(text, (x_positions[check], y_positions["released"]))

                pygame.display.flip()

                # 60 fps
                clock.tick(60)
