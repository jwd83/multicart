# description: this file contains lists of words that are used to generate random user and lobby names

import random

adjectives = [
    "adventurous",
    "airy",
    "bold",
    "breezy",
    "captivating",
    "charming",
    "chic",
    "clever",
    "curious",
    "daring",
    "dazzling",
    "debonair",
    "dramatic",
    "dreamy",
    "eccentric",
    "effervescent",
    "enchanting",
    "ethereal",
    "exuberant",
    "fascinating",
    "fearless",
    "fiery",
    "flamboyant",
    "genuine",
    "glamorous",
    "glowing",
    "hypnotic",
    "ingenious",
    "intriguing",
    "lively",
    "luminous",
    "mysterious",
    "quirky",
    "quixotic",
    "radiant",
    "ravishing",
    "sassy",
    "savvy",
    "sophisticated",
    "sultry",
    "tenacious",
    "vibrant",
    "vigorous",
    "vivacious",
    "whimsical",
    "winsome",
    "witty",
    "youthful",
    "zealous",
]

animals = [
    "aardvark",
    "albatross",
    "anteater",
    "armadillo",
    "axolotl",
    "baboon",
    "badger",
    "barracuda",
    "beaver",
    "bird",
    "bison",
    "cat",
    "cheetah",
    "chinchilla",
    "chipmunk",
    "dog",
    "dolphin",
    "elephant",
    "fennec fox",
    "fish",
    "flamingo",
    "gazelle",
    "hedgehog",
    "ibex",
    "iguana",
    "jaguar",
    "kangaroo",
    "kinkajou",
    "koala",
    "lemur",
    "llama",
    "manatee",
    "marmot",
    "meerkat",
    "mink",
    "mongoose",
    "narwhal",
    "numbat",
    "ocelot",
    "okapi",
    "ostrich",
    "pangolin",
    "penguin",
    "puma",
    "quokka",
    "rattlesnake",
    "siamang",
    "takin",
    "tarsier",
    "toucan",
    "uakari",
    "vulture",
    "wallaby",
    "wombat",
    "xerus",
    "yak",
    "zebra",
]

places = [
    "academy",
    "bakery",
    "bar",
    "cafe",
    "canyon",
    "castle",
    "cathedral",
    "cave",
    "cinema",
    "city",
    "clinic",
    "college",
    "cove",
    "desert",
    "forest"
    "fortress",
    "hospital",
    "hostel",
    "hotel",
    "inn",
    "institute",
    "laboratory",
    "library",
    "lodge",
    "motel",
    "museum",
    "observatory",
    "palace",
    "park",
    "pharmacy",
    "pub",
    "restaurant",
    "school",
    "tavern",
    "theater",
    "town",
    "university",
    "valley",
    "village",
    "workshop",
    "yard",
    "zoo",
]

nouns = [
    *animals, *places
]

def string_builder(fields: str):
    """
    fields: str
    A string of characters to provide an order to build a random string from.

    Each character in the string represents a list of words to choose from.

    The order of the characters in the string determines the order of the words in the final string.

    The characters are as follows:

    a: adjectives
    i: animals
    n: nouns
    p: places

    """

    selections = []

    for field in fields:
        if field == 'a':
            selections.append(random.choice(adjectives))
        elif field == 'i':
            selections.append(random.choice(animals))
        elif field == 'n':
            selections.append(random.choice(nouns))
        elif field == 'p':
            selections.append(random.choice(places))



    return " ".join(selections)

def _test_string_builder(query: str):
    print(f"Query: {query}, Result: {string_builder(query)}")

if __name__ == "__main__":
    _test_string_builder('ai')
    _test_string_builder('ai')
    _test_string_builder('an')
    _test_string_builder('an')
    _test_string_builder('ani')
    _test_string_builder('ani')
    _test_string_builder('aninp')
    