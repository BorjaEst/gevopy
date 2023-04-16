"""The :mod:`selection` module is intended to contain abstract and specific
classes to design your evolution algoritms.

Selection is the stage of a genetic algorithm in which individual genomes
are chosen from a population for later breeding (using the crossover operator).

A rework form:
https://github.com/DEAP/deap/blob/master/deap/tools/selection.py
"""
# pylint: disable=too-few-public-methods

import builtins
import inspect
import itertools
import math
import random
import types
from abc import ABC, abstractmethod

import numpy as np

from . import Pool

methods = {"Ponderated", "Uniform", "Best", "Worst", "Tournaments"}
__all__ = methods.union({"Selection"})


class Selection(ABC):
    """A generic selection objext that returns an specific amount of genotypes
    from a pool according to their scores. The main objective of this
    selection procedure is to keep, crossover or mutate only those genotypes
    that perform better on the solution of a problem or environment.
    """

    @abstractmethod
    def __call__(self, pool, n):
        """Executes the selection.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to select
        :returns: List with **n** selected genotypes
        """
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct Selection type."""
        if not isinstance(value, cls):
            raise TypeError("'Selection' type required")
        return value


class Ponderated(Selection):
    """Select *n* random genotypes where each genotype probability is
    ponderated by the normalized score (score[i]/sum(scores)). The list
    returned contains references to the *pool genotypes*.
    """

    def __call__(self, pool, n):
        """Executes the selection of 'n' genotypes from a pool.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to select
        :returns: A list of selected genotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 0:
                raise ValueError("Value for 'n' cannot be lower than 0")

        sum_scores = sum(pool.scores)
        try:  # Divide R[0,1] segment with normalised genotypes weigths
            n_scores = [score / sum_scores for score in pool.scores]
            n_prb = list(itertools.accumulate(n_scores))
        except ZeroDivisionError:
            return Uniform.__call__(self, pool, n)

        def choose(p):  # next avoids generating the whole list
            return next(x for x, r in zip(pool, n_prb) if r > p)
        return [choose(p).item for p in np.random.rand(n)]


class Uniform(Selection):
    """Select *n* random genotypes where each genotype probability is
    equal. The list returned contains references to the *pool genotypes*.
    """

    def __call__(self, pool, n):
        """Executes the selection of 'n' genotypes from a pool.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to select
        :returns: A list of selected genotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 0:
                raise ValueError("Value for 'n' cannot be lower than 0")

        return [random.choice(pool).item for _ in range(n)]


class Best(Selection):
    """Returns the best genotype among the input *genotypes* `n` times.
    The returned list contains references to the input *genotype*.
    """

    def __call__(self, pool, n):
        """Executes the selection of 'n' genotypes from a pool.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to return
        :returns: A list of selected genotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 0:
                raise ValueError("Value for 'n' cannot be lower than 0")

        return [pool[0].item for _ in range(n)]


class Worst(Selection):
    """Returns the worst genotype among the input *genotypes* `n` times.
    The returned list contains references to the input *genotype*.
    """

    def __call__(self, pool, n):
        """Executes the selection of 'n' genotypes from a pool.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to return
        :returns: A list of selected genotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 0:
                raise ValueError("Value for 'n' cannot be lower than 0")

        return [pool[-1].item for _ in range(n)]


class Tournaments(Selection):
    """Select the best genotype among *tournsize* randomly chosen genotypes,
    *n* times. The list returned contains references to the input *genotypes*.
    """

    def __init__(self, tournsize=lambda n: math.floor(math.sqrt(n))):
        """Selection constructor for tournaments. It takes an optional
        parameter **tournsize** which defines or calculates the size of
        each  tournament participants.
        :param tournsize: Positive number or function, default is the square
        root floor of **n**.
        """
        match type(tournsize):
            case builtins.int if tournsize <= 1:
                raise ValueError("'tournsize' cannot be lower than 1")
            case builtins.int:
                self.tournsize = lambda _: tournsize
            case types.LambdaType:
                if len(inspect.signature(tournsize).parameters) != 1:
                    raise ValueError("Arity for 'tournsize' must be 1")
                self.tournsize = tournsize
            case _:
                raise ValueError("'tournsize' must be 'int' or 'LambdaType'")

    def __call__(self, pool, n):
        """Executes the selection of 'n' genotypes from a pool.
        :param pool: A Pool of genotypes.
        :param n: The number of genotypes to select
        :returns: A list of selected genotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 0:
                raise ValueError("Value for 'n' cannot be lower than 0")
        tournsize = self.tournsize(n)

        def tournament():
            return [random.choice(pool) for _ in range(tournsize)]

        aspirants = [tournament() for _ in range(n)]
        return [max(x, key=lambda x: x.score).item for x in aspirants]
