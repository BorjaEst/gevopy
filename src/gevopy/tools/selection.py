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
from abc import abstractmethod

import numpy as np

from . import Pool

methods = {"Ponderated", "Uniform", "Best", "Worst", "Tournaments"}
__all__ = methods.union({"Selection"})


class Selection(object):
    """A generic selection objext that returns an specific amount of phenotypes
    from a pool according to their scores. The main objective of this
    selection procedure is to keep, crossover or mutate only those phenotypes
    that perform better on the solution of a problem or environment.
    """

    @abstractmethod
    def __init__(self):
        """Selection generic constructor."""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, pool, n):
        """Executes the selection.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to select
        :returns: List with **n** selected phenotypes
        """
        raise NotImplementedError


class Ponderated(Selection):
    """Select *n* random phenotypes where each phenotype probability is
    ponderated by the normalized score (score[i]/sum(scores)). The list
    returned contains references to the *pool phenotypes*.
    """

    def __init__(self):
        """Selection generic constructor."""

    def __call__(self, pool, n):
        """Executes the selection of 'n' phenotypes from a pool.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to select
        :returns: A list of selected phenotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 1:
                raise ValueError("Value for 'n' cannot be lower than 1")

        sum_scores = sum(pool.scores())
        try:  # Divide R[0,1] segment with normalised phenotypes weigths
            n_scores = [score / sum_scores for score in pool.scores()]
            n_prb = list(itertools.accumulate(n_scores))
        except ZeroDivisionError:
            return Uniform.__call__(self, pool, n)

        def choose(p):  # next avoids generating the whole list
            return next(x for x, r in zip(pool, n_prb) if r > p)
        return [choose(p) for p in np.random.rand(n)]


class Uniform(Selection):
    """Select *n* random phenotypes where each phenotype probability is
    equal. The list returned contains references to the *pool phenotypes*.
    """

    def __init__(self):
        """Selection generic constructor."""

    def __call__(self, pool, n):
        """Executes the selection of 'n' phenotypes from a pool.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to select
        :returns: A list of selected phenotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 1:
                raise ValueError("Value for 'n' cannot be lower than 1")

        return [random.choice(pool) for _ in range(n)]


class Best(Selection):
    """Returns the best phenotype among the input *phenotypes* `n` times.
    The returned list contains references to the input *phenotype*.
    """

    def __init__(self):
        """Selection generic constructor."""

    def __call__(self, pool, n):
        """Executes the selection of 'n' phenotypes from a pool.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to return
        :returns: A list of selected phenotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 1:
                raise ValueError("Value for 'n' cannot be lower than 1")

        return [pool[0] for _ in range(n)]


class Worst(Selection):
    """Returns the worst phenotype among the input *phenotypes* `n` times.
    The returned list contains references to the input *phenotype*.
    """

    def __init__(self):
        """Selection generic constructor."""

    def __call__(self, pool, n):
        """Executes the selection of 'n' phenotypes from a pool.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to return
        :returns: A list of selected phenotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 1:
                raise ValueError("Value for 'n' cannot be lower than 1")

        return [pool[-1] for _ in range(n)]


class Tournaments(Selection):
    """Select the best phenotype among *tournsize* randomly chosen phenotypes,
    *n* times. The list returned contains references to the input *phenotypes*.
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
                raise ValueError(
                    "Value for 'tournsize' cannot be lower than 1")
            case builtins.int:
                self.tournsize = lambda _: tournsize
            case builtins.callable if len(inspect.signature(tournsize).parameters) != 1:
                raise ValueError("Arity for 'tournsize' must be 1")
            case builtins.callable:
                self.tournsize = tournsize
            case _wrong_type:
                raise ValueError(
                    "Type for 'tournsize' must be 'int' or 'callable'")

    def aspirants(self, pool, n):
        """Collects a random list of aspirants with their score.
        :param pool: A Pool of phenotypes
        :param n: The number of phenotypes to select
        :returns: A list of random phenotypes with their score
        """
        return Uniform.__call__(self, pool, n)

    def __call__(self, pool, n):
        """Executes the selection of 'n' phenotypes from a pool.
        :param pool: A Pool of phenotypes.
        :param n: The number of phenotypes to select
        :returns: A list of selected phenotypes.
        """
        match (pool, n):
            case _ if not isinstance(pool, Pool):
                raise ValueError("Expected type 'Pool' for 'pool'")
            case _ if not isinstance(n, int):
                raise ValueError("Expected type 'int' for 'n'")
            case _ if not n >= 1:
                raise ValueError("Value for 'n' cannot be lower than 1")

        tournsize = self.tournsize(n)
        tournaments = [self.aspirants(pool, tournsize) for _ in range(n)]
        return [max(x, key=lambda x: x.score) for x in tournaments]
