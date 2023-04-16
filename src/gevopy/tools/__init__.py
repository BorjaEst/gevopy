"""Evolution Algorithms, Tools subpackage."""

import collections
import heapq

import sortedcontainers
from typing import Any


class PoolItem():
    """PoolItem is a tuple which contains a score on first possition and a
    item (expected genotype) on the second.
    """

    def __init__(self, score: float, item: Any):
        self.score = float(score)
        self.item = item


class Pool(sortedcontainers.SortedKeyList):
    """Pool is a sorted list of dictionaries where items are composed
    by a *score* and a *genotype.
    """

    def __init__(self, iterable=None):
        """Constructor for a pool as sorted mutable sequence.
        :param iterable: Iterable of pool items to initialize the sorted-key list
        """
        super().__init__(iterable, key=lambda pool_item: -pool_item.score)

    @property
    def scores(self):
        """Returns a sorted list of genotype scores from highest to lowest.
        :return: List of floats
        """
        return [x.score for x in self]

    @property
    def items(self):
        """Returns a sorted list of genotypes from highest to lowest.
        :return: List of any objects
        """
        return [x.item for x in self]

    def __repr__(self) -> str:
        return self.items.__repr__()

    def append(self, value):
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def extend(self, values):
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def insert(self, index, value):
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def reverse(self):
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct Pool type."""
        if not isinstance(value, cls):
            raise TypeError("'Pool' type required")
        return value


class HallOfFame(collections.abc.Sequence):
    """The hall of fame contains the best individual that ever lived in an
    evolution context (for example an algorithm). It is sorted at all time
    so that the first element of the hall of fame is the item that contains
    the genotype with the best score.

    The update is made so that old genotypes have priority on new genotypes.
    The class :class:`HallOfFame` provides an interface similar to a list
    (without being one completely). It is possible to retrieve its length,
    to iterate on it forward and backward and to get an item or a slice.
    """

    def __init__(self, maxsize):
        """Hall of fame constructor.
        :param maxsize: Maximum number of genotypes to keep in the hall
        """
        self.__items = []
        self.maxsize = maxsize

    @property
    def maxsize(self):
        """Property that defines the maximum ammount of genotypes in the hall.
        :return: Maximum allowed number of genotypes in the hall
        """
        return self.__maxsize

    @maxsize.setter
    def maxsize(self, value):
        match value:
            case _ if not isinstance(value, int):
                raise ValueError("Expected type 'int' for maxsize")
            case _ if not value > 0:
                raise ValueError("Expected maxsize value higher than 0")
            case _ if value < len(self):
                self.__items = self[:value]
        self.__maxsize = value

    def __iter__(self):
        return iter(self.__items)

    def __contains__(self, value):
        return value in self.__items

    def __getitem__(self, index):
        return self.__items.__getitem__(index)

    def __len__(self):
        return self.__items.__len__()

    def __repr__(self) -> str:
        return self.__items.__repr__()

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct HallOfFame type."""
        if not isinstance(value, cls):
            raise TypeError("'HallOfFame' type required")
        return value

    def update(self, pool):
        """Updates genotypes to the hall of fame by replacing the worst
        genotypes in the hall by the best genotypes present in pool. Old
        genotypes have preference over new genotypes.
        :param pool: A pool of genotypes
        """
        if not isinstance(pool, Pool):
            raise TypeError("Expected type 'Pool' for genotypes pool")
        records = heapq.merge(self, pool, key=lambda x: -x.score)
        self.__items = [x for _, x in zip(range(self.maxsize), records)]
