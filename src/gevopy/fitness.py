"""The :mod:`fitness` module is intended to contain parent classes to create
the procedures required to evaluate the experiment genotypes for evolution.

Similarly to the rest of modules in this library, a class desing is selected
so the user can define multiple methods to obtain a highly customisable
fitness object. Similar aproaches are commonly used in python, such for
example Unittests.

A rework form:
https://github.com/DEAP/deap/blob/master/deap/base.py
"""

from abc import ABC, abstractmethod

from dask import compute, delayed

from gevopy import genetics, tools


class _HasCache():
    """Extend class Fitness with cache properties."""

    def __init__(self, *args, cache: bool = False, **kwargs) -> None:
        """Generic constructor for fitness objects.
        :param cache: Enables cache with True, default is False
        """
        super().__init__(*args, **kwargs)
        self.cache = cache

    @property
    def cache(self):
        """Returns a boolean value indicating if score cache is enabled.
        :return: True if score cache is enabled, otherwise False
        """
        return self._cv is not None

    @cache.setter
    def cache(self, value):
        """Enables or disables cache on the fitness object.
        :param value: True to enable cache, otherwise False
        """
        if not isinstance(value, bool):
            raise ValueError("Expected 'bool' type for cache")
        self._cv = {} if value else None


class _HasScheduler():
    """Extend class Fitness dask scheduler properties."""
    scheduler_options = ['synchronous', 'threads', 'processes']

    def __init__(self, *args, scheduler: str = "threads", **kwargs) -> None:
        """Generic constructor for fitness objects.
        :param scheduler: Dask scheduler to use during fitness evaluation
        """
        super().__init__(*args, **kwargs)
        self.scheduler = scheduler

    @property
    def scheduler(self):
        """Returns the configured value for dask scheduler in the object.
        :return: A string containing one of the 'scheduler_options'
        """
        return self.__scheduler

    @scheduler.setter
    def scheduler(self, value):
        """Configures/edits the dask scheduler for genotypes evaluation.
        :param value: A string containing one of the 'scheduler_options'
        """
        if value not in self.scheduler_options:
            raise ValueError(f"Unknown '{value}' value for scheduler")
        self.__scheduler = value


class FitnessModel(_HasCache, _HasScheduler, ABC):
    """Fitness base class to run genotypes evaluation.
    It requires the user to define a `score` method which takes a genotype
    as input and returns its score value. Use cache and scheduler to control
    how the evaluation is executed:

      - If genotype score does not change between generations, you can use
        `cache=True` to skip score computation on those genotypes whose id
        has been already evaluated.

      - If genotypes interact between them, or have some waiting times on
        the evaluation process, you might want to set `scheduler="threads"`
        to run multiple genotypes in parallel. Scheduler is based on Dask,
        see https://docs.dask.org/en/stable/scheduling.html

    Additionally you can configure a setUp function which would be executed
    once, before evaluating the genotypes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, genotypes):
        """Fitness call to calculate genotype scores.
        :param genotypes: List with genotypes to score
        :return: Pool with genotypes
        """
        self.setup(genotypes)
        delayeds = [delayed(self.worker)(ph) for ph in genotypes]
        scores = compute(*delayeds, scheduler=self.scheduler)
        pool = tools.Pool([tools.PoolItem(*x) for x in zip(scores, genotypes)])
        if self.cache:
            self._cv = {x.item.id: x.score for x in pool}
        return pool

    def setup(self, genotypes):
        """Fitness function designed to prepare the genotypes evaluation.
        :param genotypes: List with genotypes to score
        """
        pass  # pylint: disable=unnecessary-pass

    def worker(self, genotype):
        """Fitness wrap to return cached score value if configured.
        :param genotype: genotype to evaluate
        :return: genotype score
        """
        if self.cache and genotype.id in self._cv:
            return self._cv[genotype.id]
        else:
            return self.score(genotype)

    @abstractmethod
    def score(self, genotype):
        """Abstract function to return the score value of a genotype.
        :param genotype: genotype to evaluate
        :return: genotype score
        """
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct FitnessModel type."""
        if not isinstance(value, cls):
            raise TypeError("'FitnessModel' type required")
        return value
