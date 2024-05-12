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

creatures = [
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
    "cougar",
    "coyote",
    "crab",
    "crane",
    "crow",
    "deer",
    "dog",
    "dolphin",
    "dragon",
    "duck",
    "elephant",
    "fish",
    "flamingo",
    "fox",
    "gazelle",
    "hedgehog",
    "ibex",
    "iguana",
    "jaguar",
    "jellyfish",
    "kangaroo",
    "kinkajou",
    "koala",
    "lemur",
    "llama",
    "manatee",
    "marmot",
    "meerkat",
    "mole",
    "monkey",
    "mink",
    "mongoose",
    "narwhal",
    "numbat",
    "ocelot",
    "okapi",
    "ostrich",
    "pangolin",
    "panther",
    "penguin",
    "puma",
    "quokka",
    "snake",
    "tarsier",
    "toucan",
    "vulture",
    "wallaby",
    "wombat",
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
    *creatures, *places
]

def string_builder(fields: str):
    """
    fields: str
    A string of characters to provide an order to build a random string from.

    Each character in the string represents a list of words to choose from.

    The order of the characters in the string determines the order of the words in the final string.

    The characters are as follows:

    a: adjectives
    c: creatures
    n: nouns
    p: places

    """

    selections = []

    for field in fields:
        if field == 'a':
            selections.append(random.choice(adjectives))
        elif field == 'c':
            selections.append(random.choice(creatures))
        elif field == 'n':
            selections.append(random.choice(nouns))
        elif field == 'p':
            selections.append(random.choice(places))



    return " ".join(selections)

def _test_string_builder(query: str):
    print(f"Query: {query}, Result: {string_builder(query)}")

if __name__ == "__main__":
    _test_string_builder('ac')
    _test_string_builder('ac')
    _test_string_builder('an')
    _test_string_builder('an')
    _test_string_builder('anc')
    _test_string_builder('anc')
    _test_string_builder('acnp')
