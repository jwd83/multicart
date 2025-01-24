import sys
import os


def help():
    print(
        """
Usage: python main.py <command> [args]

Commands:
help                    Show this help message
scene new               Make a new scene
scene run <scene_name>  Run the game with the specified scene
scene list              List all the scenes
"""
    )


def start_game():
    from game import Game
    import asyncio

    asyncio.run(Game().run())
    sys.exit(0)


def scene():
    if len(sys.argv) < 3:
        print("Missing argument")
        sys.exit(1)

    if sys.argv[2] == "new":
        scene_new()


def scene_new():

    folder = "scenes/" + input("Folder for scene? (Default=None, bad idea):")
    folder = folder.strip()
    name = input("Name of the Scene? (CamelCasePlease):")
    filename = name.lower() + ".py"
    # check if a folder was specified and check if it exists
    if folder.strip() != "scenes/":
        folder += "/"
        if not os.path.exists(folder):
            if input("Folder does not exist, create it? (y/N)").lower() != "y":
                sys.exit(1)
            os.makedirs(folder)
    file_path = folder + filename

    # check if the file already exists
    if os.path.exists(file_path):
        print(f"File {file_path} already exists")
        sys.exit(1)

    # load the blank scene template, replace it's name with the class
    # name and write it to the file_path
    with open("scenes/blank.py") as f:
        content = f.read()
        content = content.replace("Blank", name)
        with open(file_path, "w") as f:
            f.write(content)

    # append a new import statement for the scene into scenes/__init__.py
    with open("scenes/__init__.py", "a") as f:
        # remove the leading scenes/ from the folder
        import_path = (
            "." + folder.replace("scenes/", "").replace("/", ".") + name.lower()
        )
        f.write(f"\nfrom {import_path} import {name} # auto-generated")


def main():
    # check if we got any command line arguments
    if len(sys.argv) <= 1:
        # moved this here for the speedup
        start_game()

    if sys.argv[1] == "help":
        help()
    elif sys.argv[1] == "scene":
        scene()
    else:
        print("Unrecognized command")


if __name__ == "__main__":
    main()
