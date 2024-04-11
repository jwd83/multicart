from ast import parse
import sys

class GameController:
    def __init__(self, joystick, mappings):
        self.joystick = joystick
        self.mappings = mappings
        self.reset()

    def reset(self):
        self.held = []
        self.pressed = []
        self.released = []
        self.l_trigger = 0.0
        self.r_trigger = 0.0
        self.l_thumb = (0.0, 0.0)
        self.r_thumb = (0.0, 0.0)
        self.hat = (0, 0)


    def update(self):
        self.reset()

        



# returns the string representation of the platform the script is running on
# in the format expected by the gamecontrollerdb.txt file. Returns 'unknown' if
# the platform is not recognized.
def parse_file(field, value):

    platform = get_platform()

    lines = None

    # load the gamecontrollerdb.txt file
    with open('gamecontrollerdb.txt', 'r') as file:
        lines = file.readlines()

    # iterate through the lines of the file
    if lines is None:
        return None

    for line in lines:

        # skip comments
        if line.startswith('#'):
            continue

        # skip any blank lines
        if line.strip() == '':
            continue

        # split the line into fields
        fields = line.split(',')
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
        if field == 'guid':
            if l_guid == value:
                match_found = True

        elif field == 'name':
            if l_name == value:
                match_found = True

        # if we found a match, return the mappings
        if match_found:
            print(f"Match found: {l_name} [{l_guid}] on {l_platform}")
            return l_mappings

        # print(f"Processing line. Fields count: {fields_count}, guid: {l_guid}, name: {l_name}, mappings: {l_mappings}, platform: {l_platform}")
        # sys.exit(0)
    return None

def mappings_by_name(name):
    return parse_file('name', name)


def mappings_by_guid(guid):
    return parse_file('guid', guid)


def get_platform():

    platform = sys.platform

    if platform.startswith('win32'):
        return 'Windows'
    elif platform.startswith('darwin'):
        return 'Mac OS X'
    elif platform.startswith('linux'):
        return 'Linux'
    else:
        # default to windows if we can't determine the platform
        return 'unknown'


if __name__ == '__main__':
    print("Detected: " + get_platform())
    print(mappings_by_guid('03000000c82d00000161000000010000'))
    print(mappings_by_name('8BitDo SN30 Pro'))



