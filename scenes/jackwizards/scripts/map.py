# rework of the map maker from my rogue-map project i was using to teach kayla a map
# generator for her game

import numpy as np

# count the number of rooms in the map
def count_rooms(floor_map: np.ndarray) -> int:

    return len(floor_map.nonzero()[0])

# count the number of dead ends in the map
def count_dead_ends(floor_map: np.ndarray) -> int:
    dead_ends = 0
    for x in range(floor_map.shape[0]):
        for y in range(floor_map.shape[1]):
            room_flags = floor_map[x, y] & 31
            if room_flags in [1, 2, 4, 8]:
                dead_ends += 1
    return dead_ends

def potential_dead_ends(floor_map: np.ndarray) -> list:
    # make our potential dead end list
    pde = []

    avoid = [0, 1, 2, 4, 8]

    for x in range(1, floor_map.shape[0] - 1):
        for y in range(1, floor_map.shape[1] - 1):
            # if we find an empty space
            if floor_map[x, y] == 0:
                if (floor_map[x - 1, y] not in avoid or
                    floor_map[x, y - 1] not in avoid or
                    floor_map[x + 1, y] not in avoid or
                    floor_map[x, y + 1] not in avoid
                ):
                    pde.append((x, y))

    return pde


# Create a map starting with a 16x16 or user defined size
# using the "drunken walk" algorithm, create a random path
# through the map. bits of a room will represent it's connection
# starting at 12 o;clock and moving clockwise the bits will be
# as follows: 1 = up, 2 = right, 4 = down, 8 = left
#
# bits above the 8 value will be used for...
# 16 = starting room where the player spawns
# 32 = boss room
# 64 = compass room
# 128 = map room
#
# Any value with a bit set at all will be considered a room
# and it's connections will be determined by the bits set.
def make_floor(minimum_rooms=10, desired_dead_ends=3, size=16):

    if minimum_rooms > size * size:
        minimum_rooms = size * size

    if desired_dead_ends < 3:
        desired_dead_ends = 3

    midpoint = int(size / 2)

    x = midpoint
    y = midpoint

    # generate the empty map
    floor_map = np.zeros((size, size), dtype=int)

    # set the starting room bit
    floor_map[x, y] |= 16

    while count_rooms(floor_map) < minimum_rooms:

        # randomly choose a direction to move
        direction = np.random.choice(["up", "down", "left", "right"])

        if direction == "up" and y > 0:
            floor_map[x, y] |= 1
            y -= 1
            floor_map[x, y] |= 4
        elif direction == "right" and x < size - 1:
            floor_map[x, y] |= 2
            x += 1
            floor_map[x, y] |= 8
        elif direction == "down" and y < size - 1:
            floor_map[x, y] |= 4
            y += 1
            floor_map[x, y] |= 1
        elif direction == "left" and x > 0:
            floor_map[x, y] |= 8
            x -= 1
            floor_map[x, y] |= 2


    # loop through the map and find 0s next to values that
    # are not 1,2,4 or 8 and create a room adjacent to them
    # to increase the number of dead ends.
    avoid = [0, 1, 2, 4, 8]

    # new code to add dead ends to the map
    while desired_dead_ends > count_dead_ends(floor_map) and len(potential_dead_ends(floor_map)) > 0:
        print("Potential dead ends:")
        pde = potential_dead_ends(floor_map)
        print(pde)
        x, y = pde[np.random.choice(len(pde))]

        print(f"Adding dead end at {x}, {y}")

        # check to the left first
        if floor_map[x - 1, y] not in avoid:
            # if there is an existing room that's
            # not already a dead end, add a dead end
            # to it's right
            floor_map[x - 1, y] |= 2
            floor_map[x, y] |= 8

        # if not to the left then check above
        elif floor_map[x, y - 1] not in avoid:
            # if there is an existing room that's
            # not already a dead end, add a dead end
            floor_map[x, y - 1] |= 4
            floor_map[x, y] |= 1

        # if not above or to the left then check to the right
        elif floor_map[x + 1, y] not in avoid:
            # if there is an existing room that's
            # not already a dead end, add a dead end
            floor_map[x + 1, y] |= 8
            floor_map[x, y] |= 2
        # if not any of those then check finally check below
        elif floor_map[x, y + 1] not in avoid:
            # if there is an existing room that's
            # not already a dead end, add a dead end
            floor_map[x, y + 1] |= 1
            floor_map[x, y] |= 4


    # set the boss room as the furthest dead end room from the starting room

    # variables to hold the furthest room from the starting room
    search_x = midpoint
    search_y = midpoint
    search_distance = 0

    # loop through the map and find the furthest room from the starting room
    # to place the boss in.
    for x in range(floor_map.shape[0]):
        for y in range(floor_map.shape[1]):
            if floor_map[x, y] in [1, 2, 4, 8]:
                distance = abs(midpoint - x) + abs(midpoint - y)
                if distance > search_distance:
                    search_x = x
                    search_y = y
                    search_distance = distance

    floor_map[search_x, search_y] |= 32

    # place the compass room in the room closest dead end to the starting room
    search_x = midpoint
    search_y = midpoint
    search_distance = size * 4 # set to a high value to ensure the first room is closer

    for x in range(floor_map.shape[0]):
        for y in range(floor_map.shape[1]):
            if floor_map[x, y] in [1, 2, 4, 8]:
                distance = abs(midpoint - x) + abs(midpoint - y)
                if distance < search_distance:
                    search_x = x
                    search_y = y
                    search_distance = distance

    floor_map[search_x, search_y] |= 64


    # place the map room in the next closest dead end to the starting room
    search_x = midpoint
    search_y = midpoint
    search_distance = size * 4 # set to a high value to ensure the first room is closer

    for x in range(floor_map.shape[0]):
        for y in range(floor_map.shape[1]):
            if floor_map[x, y] in [1, 2, 4, 8]:
                distance = abs(midpoint - x) + abs(midpoint - y)
                if distance < search_distance:
                    search_x = x
                    search_y = y
                    search_distance = distance

    floor_map[search_x, search_y] |= 128



    print("Final map:")
    print(floor_map)
    print("Final Stats:")
    print("Rooms: ", count_rooms(floor_map))
    print("Dead Ends: ", count_dead_ends(floor_map))

    return floor_map

