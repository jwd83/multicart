import sys
import os


def help():
    print(
        """
Usage: python main.py <command> [args]

Commands:
>> General
help                            Show this help message

>> Scene Commands
scene new                       Make a new scene
scene run <scene_name>          Run the game with the specified scene
scene list                      List all the scenes

>> Sprite Commands
dice <image.png> <width> <height> <output_folder>
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
    elif sys.argv[2] == "list":
        scene_list()


def scene_list():
    """List all detected scenes by parsing scenes/__init__.py and scanning for unregistered ones"""
    import re

    # Parse registered scenes from __init__.py
    registered = {}  # class_name -> module_path

    with open("scenes/__init__.py") as f:
        for line in f:
            # Match import patterns like:
            # from .folder.module import ClassName
            # from scenes.module import ClassName
            match = re.match(
                r"from\s+([\w.]+)\s+import\s+(\w+)", line.strip()
            )
            if match:
                module_path, class_name = match.groups()
                # Clean up module path for display
                module_path = module_path.lstrip(".")
                module_path = module_path.replace("scenes.", "")
                registered[class_name] = module_path

    # Scan for all scene classes in the scenes directory
    all_scenes = {}  # class_name -> (module_path, file_path)
    scene_class_pattern = re.compile(r"^class\s+(\w+)\s*\(\s*Scene\s*\)\s*:")

    for root, dirs, files in os.walk("scenes"):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if not file.endswith(".py"):
                continue
            if file.startswith("__") or file == "blank.py":
                continue

            file_path = os.path.join(root, file)
            # Convert file path to module path
            module_path = file_path.replace("scenes/", "").replace("/", ".").replace("\\", ".")[:-3]

            with open(file_path) as f:
                try:
                    content = f.read()
                    for match in scene_class_pattern.finditer(content):
                        class_name = match.group(1)
                        all_scenes[class_name] = (module_path, file_path)
                except Exception:
                    pass

    # Find unregistered scenes
    unregistered = []
    for class_name, (module_path, file_path) in all_scenes.items():
        if class_name not in registered:
            unregistered.append((class_name, module_path, file_path))

    # Sort both lists
    registered_list = sorted(registered.items(), key=lambda x: x[0].lower())
    unregistered.sort(key=lambda x: x[0].lower())

    # Calculate column width
    all_names = [name for name, _ in registered_list] + [name for name, _, _ in unregistered]
    max_name_len = max(len(n) for n in all_names) if all_names else 0

    # Print registered scenes
    print(f"\nRegistered Scenes ({len(registered_list)}):\n")
    print(f"{'Scene Name':<{max_name_len + 2}} Module Path")
    print("-" * (max_name_len + 2 + 35))

    for class_name, module_path in registered_list:
        print(f"{class_name:<{max_name_len + 2}} {module_path}")

    # Print unregistered scenes if any
    if unregistered:
        print(f"\nUnregistered Scenes ({len(unregistered)}):\n")
        print(f"{'Scene Name':<{max_name_len + 2}} File Path")
        print("-" * (max_name_len + 2 + 35))

        for class_name, module_path, file_path in unregistered:
            print(f"{class_name:<{max_name_len + 2}} {file_path}")

        print("\nTo register a scene, add an import to scenes/__init__.py")
    else:
        print("\nAll scenes are registered.")

    print()


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


def dice():
    print("Slice and dice a sprite sheet you say? I'm on it!")
    sys.exit(0)


def main():
    # check if we got any command line arguments
    if len(sys.argv) <= 1:
        # moved this here for the speedup
        start_game()

    if sys.argv[1] == "help":
        help()
    elif sys.argv[1] == "scene":
        scene()
    elif sys.argv[1] == "dice":
        dice()
    else:
        print("Unrecognized command")


if __name__ == "__main__":
    main()
