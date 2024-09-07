import random

from hashlib import md5


class Seed:
    """
    This class represents a Seed object.

    Attributes:
        __seed (str): The seed value. Default is None which
        generates a random seed.

    Methods:
        get_seed(): Returns the current seed value.
        set_seed(seed: str): Sets a new seed value.
    """

    def __init__(self, seed: str | None = None):
        """
        The constructor for Seed class.

        Parameters:
            seed (str): The seed value. Default is "Peach".
        """
        if seed is None:
            # generate a random string to be used as a seed
            self.__seed = str(random.random())
        else:
            self.__seed = seed

    def get_seed(self):
        """
        The function to get the current seed value.

        Returns:
            str: The current seed value.
        """
        return self.__seed

    def set_seed(self, seed: str = "Peach"):
        """
        The function to set a new seed value.

        Parameters:
            seed (str): The new seed value. Default is "Peach".
        """
        self.__seed = seed

    def __hashed(self, name: str = "default"):
        """
        The function to return a hashed value based on the seed and the name.
        """

        # generate md5 hash from the seed and the name
        result = md5((self.__seed + name).encode()).hexdigest()
        # print("Seed: ", self.__seed, "Name: ", name, "Hash: ", result)
        return result

    def float(self, name: str = "default") -> float:
        """
        The function to return a 0-1 float value based on the seed and the name.
        """

        result = self.__hashed(name)

        # convert the hash to a float value between 0 and 1
        return int(result, 16) / 16**32

    def bool(self, name: str = "default") -> bool:
        """
        The function to return a boolean value based on the seed and the name.
        """

        result = self.__hashed(name)
        return int(result, 16) % 2 == 0

    def int(self, name: str = "default", min: int = 0, max: int = 1_000_000) -> int:
        """
        The function to return an integer value based on the seed and the name.
        The minimum value is inclusive and the maximum value is exclusive.
        By default, the minimum value is 0 and the maximum value is 1,000,000.
        """

        result = self.__hashed(name)
        return int(result, 16) % (max - min) + min

    def choice(self, name: str = "default", choices: list = []) -> any:
        """
        The function to return a random choice from a list based on the seed and the name.
        """

        if len(choices) == 0:
            return None

        result = self.__hashed(name)
        return choices[int(result, 16) % len(choices)]
