# rework of the map maker from my rogue-map projet i was using to teach kayla a map
# generator for her game

import numpy as np


def count_rooms(floor_map: np.ndarray) -> int:

    return len(floor_map.nonzero()[0])


def count_dead_ends(floor_map: np.ndarray) -> int:
    dead_ends = 0
    for x in range(floor_map.shape[0]):
        for y in range(floor_map.shape[1]):
            if floor_map[x, y] == 1:
                dead_ends += 1
            elif floor_map[x, y] == 2:
                dead_ends += 1
            elif floor_map[x, y] == 4:
                dead_ends += 1
            elif floor_map[x, y] == 8:
                dead_ends += 1
    return dead_ends


# Create a map starting with a 16x16 or user defined size
# using the "drunken walk" algorithm, create a random path
# through the map. bits of a room will represent it's connection
# starting at 12 o;clock and moving clockwise the bits will be
# as follows: 1 = up, 2 = right, 4 = down, 8 = left
#
# bits above the 8 value will be used for...
# 16 = starting room
#
# Any value with a bit set at all will be considered a room
# and it's connections will be determined by the bits set.


def make_floor(minimum_rooms=10, desired_dead_ends=0, size=16):

    if minimum_rooms > size * size:
        minimum_rooms = size * size

    midpoint = int(size / 2)

    x = midpoint
    y = midpoint

    # generate the empty map
    floor_map = np.zeros((size, size), dtype=int)

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

        # # print the current stats
        # print("Rooms: ", count_rooms(floor_map))
        # print("Dead Ends: ", count_dead_ends(floor_map))


    if desired_dead_ends > count_dead_ends(floor_map):
        print("Desired minimum rooms reached. Adding dead ends. Map before adding dead ends:")
        print(floor_map)

        # loop through the map and find 0s next to values that
        # are not 1,2,4 or 8 and create a room adjancent to them
        # to increase the number of dead ends.
        avoid = [0, 1, 2, 4, 8]

        # avoid the outer edges of the map so we don't look for
        # values in positions that don't exist
        for x in range(1, floor_map.shape[0] - 1):
            for y in range(1, floor_map.shape[1] - 1):
                # if we find an empty space
                if floor_map[x, y] == 0:

                    # check the surrounding values

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

                if desired_dead_ends <= count_dead_ends(floor_map):
                    break

    # now that the set the starting room bit


    print("Final map:")
    print(floor_map)
    print("Final Stats:")
    print("Rooms: ", count_rooms(floor_map))
    print("Dead Ends: ", count_dead_ends(floor_map))

    return floor_map


def main():
    while True:
        make_floor(
            minimum_rooms=int(input("How many rooms? ")),
            desired_dead_ends=int(
                input("How many dead ends? (0 for random): ")),
        )


if __name__ == "__main__":

    main()