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
        :param iterable: Iterable of values to initialize the sorted-key list
        """
        super().__init__(iterable, key=lambda item: -item.score)

    def scores(self):
        """Returns a sorted list of phenotype scores from highest to lowest.
        :return: List of numbers (int or float)
        """
        return [item.score for item in self]

    def append(self, value):
        """Method append is unsupported on chromosome types"""
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def extend(self, values):
        """Method extend is unsupported on chromosome types"""
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def insert(self, index, value):
        """Method insert is unsupported on chromosome types"""
        raise TypeError(f"Unsupported operation by '{self.__class__}'")

    def reverse(self):
        """Method reverse is unsupported on chromosome types"""
        raise TypeError(f"Unsupported operation by '{self.__class__}'")


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
        self.__items = []
        self.maxsize = maxsize

    @property
    def maxsize(self):
        """Property that defines the maximum ammount of phenotypes in the hall.
        :return: Maximum allowed number of phenotypes in the hall
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

    def update(self, pool):
        """Updates phenotypes to the hall of fame by replacing the worst
        phenotypes in the hall by the best phenotypes present in pool. Old
        phenotypes have preference over new phenotypes.
        :param pool: A pool of phenotypes
        """
        if not isinstance(pool, Pool):
            raise TypeError("Expected type 'Pool' for phenotypes pool")
        records = heapq.merge(self, pool, key=lambda x: -x.score)
        self.__items = [x for _, x in zip(range(self.maxsize), records)]

    def __getitem__(self, index):
        """Return the phenotyp/phenotypes stored in the hall of fame. The
        hall is sorted from best (first; 0) to worst (last; N).
        :param key: Integer for the phenotype to retrieve
        :return: Phenotype at key position
        """
        return self.__items.__getitem__(index)

    def __len__(self):
        """Number of phenotypes stored at the hall of fame.
        :return: Integer indicating the number of stored phenotypes
        """
        return self.__items.__len__()

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct HallOfFame type."""
        if not isinstance(value, cls):
            raise TypeError("'HallOfFame' type required")
        return value

    def __repr__(self) -> str:
        """Representation for HallOfFame.
        :return: Classificatory representation for members
        """
        return self.__items.__repr__()
