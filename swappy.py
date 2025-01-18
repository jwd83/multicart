# swappy - my csv based color palette swapper
# swappy takes arguments for a source folder, a csv file and optionally a target folder
# if a target folder is not specified the csv file will be generated from the source folder's color palette
# if a target folder is specified the csv file will be used to swap the color palette of the images in the source folder and save them in the target folder
# the csv file will consist of the columns SourceR, SourceG, SourceB, SourceA, TargetR, TargetG, TargetB, TargetA, Notes
import csv
import os
import sys
import pygame

help_message = """
Swappy - Jared's color palette swapper created one lazy Saturday afternoon

Usage: swappy.py <source_folder> <csv_file> [target_folder]

Required arguments:
source_folder: the folder containing the images to swap the color palette of
csv_file: the csv file for color palette swapping

Optional arguments:
target_folder: the folder to save the images with the swapped color palette

When the target_folder is not specified, the csv file will be generated from
the source_folder's color palette.

When the target_folder is specified, the csv file will be used to swap the
color palette of the images in the source_folder and save them in the target_folder.

"""


def export_palette(path_source_folder, path_csv):

    # iterate through every png image in the source folder and extract the entire unique color palette
    # once extracted write the sorted palette to a csv file

    files = os.listdir(path_source_folder)
    palette = set()

    for file in files:
        if str(file).lower().endswith(".png"):
            image = pygame.image.load(os.path.join(path_source_folder, file))
            for x in range(image.get_width()):
                for y in range(image.get_height()):
                    color = image.get_at((x, y))
                    # create the rgba hex code as an 8 digit string
                    color_hex = "{:02x}{:02x}{:02x}{:02x}".format(
                        color.r, color.g, color.b, color.a
                    )
                    palette.add(color_hex)

    with open(path_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "SourceR",
                "SourceG",
                "SourceB",
                "SourceA",
                "TargetR",
                "TargetG",
                "TargetB",
                "TargetA",
                "Notes",
            ]
        )
        for color in sorted(palette):
            row = []
            for _ in range(2):
                for i in range(0, len(color), 2):
                    row.append("{:02x}".format(int(color[i : i + 2], 16)))
            row.append("")
            writer.writerow(row)


def swap_palette(path_source_folder, path_csv, path_target_folder):
    # Read the CSV file and create a mapping of source colors to target colors
    color_map = {}
    with open(path_csv, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_color = (
                int(row["SourceR"], 16),
                int(row["SourceG"], 16),
                int(row["SourceB"], 16),
                int(row["SourceA"], 16),
            )
            target_color = (
                int(row["TargetR"], 16),
                int(row["TargetG"], 16),
                int(row["TargetB"], 16),
                int(row["TargetA"], 16),
            )
            color_map[source_color] = target_color

    # Iterate through each image in the source folder and swap the colors
    files = os.listdir(path_source_folder)
    for file in files:
        if str(file).lower().endswith(".png"):
            image = pygame.image.load(os.path.join(path_source_folder, file))
            for x in range(image.get_width()):
                for y in range(image.get_height()):
                    color = image.get_at((x, y))
                    color_tuple = (color.r, color.g, color.b, color.a)
                    if color_tuple in color_map:
                        new_color = color_map[color_tuple]
                        image.set_at((x, y), new_color)
            pygame.image.save(image, os.path.join(path_target_folder, file))


def help():
    print(help_message)
    sys.exit(1)


def main():
    # parse arguments and verify the folder(s) and file(s) exist
    # if the target folder is not specified generate the csv file from the source folder
    # if the target folder is specified swap the color palette of the images in the source folder and save them in the target folder

    if not (len(sys.argv) == 3 or len(sys.argv) == 4):
        help()

    source_folder = sys.argv[1]
    csv_file = sys.argv[2]
    target_folder = sys.argv[3] if len(sys.argv) == 4 else None

    if not os.path.exists(source_folder):
        print("Source folder does not exist")
        sys.exit(1)

    if target_folder and not os.path.exists(target_folder):
        print("Target folder does not exist")
        sys.exit(1)

        # check that the csv file exists as we need to read it
        if not os.path.exists(csv_file):
            print("CSV file does not exist")
            sys.exit(1)

    if len(sys.argv) == 3:
        export_palette(source_folder, csv_file)
    else:
        target_folder = sys.argv[3]
        swap_palette(source_folder, csv_file, target_folder)


if __name__ == "__main__":
    main()
