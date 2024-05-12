# description: this file contains lists of words that are used to generate random user and lobby names

import random

class NameBuilder:
    def __init__(self):

        self.adjectives = [
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

        self.creatures = [
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

        self.places = [
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
            "forest",
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

        self.shuffle()

    def shuffle(self):
        random.shuffle(self.adjectives)
        random.shuffle(self.creatures)
        random.shuffle(self.places)

    def __next_item(self, list: list):
        a = list.pop()
        list.insert(0, a)
        return a

    def build(self, fields: str):
        """
        fields: str
        A string of characters to provide an order to build a random string from.

        Each character in the string represents a list of words to choose from.

        The order of the characters in the string determines the order of the words in the final string.

        The characters are as follows:

        a: adjectives
        c: creatures
        p: places

        """

        selections = []

        for field in fields:
            if field == 'a':
                selections.append(self.__next_item(self.adjectives))
            elif field == 'c':
                selections.append(self.__next_item(self.creatures))
            elif field == 'p':
                selections.append(self.__next_item(self.places))

        return " ".join(selections)

def _test_string_builder(query: str):
    return(f"Query: {query}, Result: {nb.build(query)}")

if __name__ == "__main__":
    nb = NameBuilder()
    for i in range(20):
        print(f"Test {i + 1}: {_test_string_builder('ac')}")
