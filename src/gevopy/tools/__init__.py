"""Evolution Algorithms, Tools subpackage."""

import heapq
from collections.abc import Sequence

from sortedcontainers import SortedKeyList


class Pool(SortedKeyList):
    """Pool is a sorted list of dictionaries where items are composed
    by a *score* and a *phenotype.
    """

    def __init__(self, iterable=None):
        """Constructor for a pool as sorted mutable sequence.
        :param iterable: Initial iterable of values to initialize the sorted-key list
        """
        super().__init__(iterable, key=lambda item: -item.score)

    def scores(self):
        """Returns a sorted list of phenotype scores from highest to lowest.
        :return: List of numbers (int or float)
        """
        return [item.score for item in self]

    def append(self, value):
        """Method append is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")

    def extend(self, values):
        """Method extend is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")

    def insert(self, index, value):
        """Method insert is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")

    def reverse(self):
        """Method reverse is unsupported on chromosome types"""
        raise AttributeError(f"Unsupported operation by '{self.__class__}'")


class HallOfFame(Sequence):
    """The hall of fame contains the best individual that ever lived in an
    evolution context (for example an algorithm). It is sorted at all time
    so that the first element of the hall of fame is the item that contains
    the phenotype with the best score.

    The update is made so that old phenotypes have priority on new phenotypes.
    The class :class:`HallOfFame` provides an interface similar to a list
    (without being one completely). It is possible to retrieve its length,
    to iterate on it forward and backward and to get an item or a slice.
    """

    def __init__(self, maxsize):
        """Hall of fame constructor.
        :param maxsize: Maximum number of phenotypes to keep in the hall
        """
        match maxsize:
            case _ if not isinstance(maxsize, int):
                raise ValueError("Expected type 'int' for maxsize")
            case _ if not maxsize > 0:
                raise ValueError("Expected maxsize value higher than 0")

        self.maxsize = maxsize
        self.__items = []

    def update(self, phenotypes, generation):
        """Updates phenotypes to the hall of fame by replacing the worst
        phenotypes in it by the best phenotypes present in *pool*. Old
        phenotypes have preference over new phenotypes.
        :param phenotypes: A list of evaluated phenotypes
        :param generation: Generation to get priority in case of draw
        """
        match (phenotypes, generation):
            case _ if not isinstance(phenotypes, list):
                raise ValueError("Expected type 'list' for phenotypes")
            case _ if not isinstance(generation, int):
                raise ValueError("Expected type 'int' for generation")
            case _ if not generation >= 0:
                raise ValueError("Value for generation cannot be lower than 0")

        def sorting(item):
            return item[0].score, -item[1]

        items = self.__items + [(x, generation) for x in phenotypes]
        self.__items = heapq.nlargest(self.maxsize, items, key=sorting)

    def __getitem__(self, key):
        """Return the phenotype stored in the hall of fame. The hall is
        sorted from best (first; 0) to worst (last; N).
        :param key: Integer for the phenotype to retrieve
        :return: Phenotype at key position
        """
        return self.__items[key][0]

    def __len__(self):
        """Number of phenotypes stored at the hall of fame.
        :return: Integer indicating the number of stored phenotypes
        """
        return len(self.__items)
