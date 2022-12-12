"""The :mod:`algorithms` module is intended to contain some specific
algorithms in order to execute the most common evolutionary algorithms.

The methods used here are more for convenience than reference as the
implementation of every evolutionary algorithm may vary infinitely. Most
of the algorithms in this module use operators registered in the tools
package.

A rework form:
https://github.com/DEAP/deap/blob/master/deap/algorithms.py
"""

import functools
import logging
import math
from abc import ABC, abstractmethod

from pydantic import BaseModel

from gevopy import tools
from gevopy.tools.crossover import Crossover
from gevopy.tools.mutation import Mutation
from gevopy.tools.selection import Selection

# https://docs.python.org/3/howto/logging-cookbook.html
module_logger = logging.getLogger(__name__)


class Algorithm(BaseModel, ABC):
    """Base abstract class for algorithms generation and identification.
    An algorithm is composed generally by at least 3 components:
     - Selection: Tool to select phenotypes
     - Crossover: Tool to crossover phenotypes
     - Mutation: Tool to mutate phenotypes

    This components can be assigned to an algorithm class by Inheritance
    using the provided classes `Has<Attribute>`. Instances from an algorithm
    can be created and edited after, but their values are limited to the
    corresponding classes from `tools` subpackage.

    .. note::
        Some optimization problems might not be suitable for crossover or
        mutation operations.

    When an algoritm has the property crossover, you can usually configure
    a second `selection` argument `selection2` to control how the algorithm 
    selects the secondary phenotype.
    """

    class Config:
        # pylint: disable=missing-class-docstring
        # pylint: disable=too-few-public-methods
        keep_untouched = (functools.cached_property,)

    @functools.cached_property
    def logger(self):
        """Experiment logger, used to trace and print experiment info.
        :return: Experiment.Logger
        """
        return logging.getLogger(f"{self.__class__}")

    def __call__(self, population):
        """Executes the algorithm to return a population offspring.
        :param population: List of phenotypes
        :returns: A list of varied phenotypes
        """
        return self.run_cycle(tools.Pool(population))

    @abstractmethod
    def run_cycle(self, phenotypes):
        """Executes an algorithm cyle to return a population offspring.
        :param phenotypes: Pool of ordered phenotypes by score
        :returns: A list of varied phenotypes
        """
        raise NotImplementedError


class HasSelection1(Algorithm):
    """Extend class Algorithm with a second selection round of phenotypes."""
    selection1: Selection

    def __init__(self, **data) -> None:
        """Generic constructor for genetic algorithms."""
        super().__init__(**data)

    def select(self, phenotypes, n):
        """Extends algorithm call method with phenotypes selection operation.
        :param phenotypes: Pool of evaluated phenotypes
        :param n: Number of phenotype to select from pool
        :returns: A list of varied phenotypes
        """
        self.logger.debug("selection1:\t%s", self.selection1)
        selected1 = self.selection1(phenotypes, n)
        self.logger.debug("selection1=\t%s", selected1)
        return selected1


class HasSelection2(HasSelection1, Algorithm):
    """Extend class Algorithm with a second selection round of phenotypes."""
    selection2: Selection

    def select(self, phenotypes, n):
        """Extends algorithm call method with phenotypes selection operation.
        :param phenotypes: Pool of evaluated phenotypes
        :param n: Number of phenotype to select from pool 
        :returns: A list of varied phenotypes
        """
        selected1 = super().select(phenotypes, n)
        self.logger.debug("selection2:\t%s", self.selection2)
        selected2 = self.selection2(phenotypes, n)
        self.logger.debug("selection2=\t%s", selected2)
        return selected1, selected2


class HasCrossover(HasSelection2, Algorithm):
    """Extend class Algorithm with crossover properties and methods."""
    crossover: Crossover

    def cross(self, selected1, selected2):
        """Extends algorithm call method with phenotypes crossover operation.
        :param selected1: List 1 of phenotypes to cross
        :param selected2: List 2 of phenotypes to cross
        :returns: A list of varied phenotypes
        """
        self.logger.debug("crossover:\t%s", self.crossover)
        selections = zip(selected1, selected2)
        offspring = [self.crossover(x, y)[0] for x, y in selections]
        self.logger.debug("offspring=\t%s", offspring)
        return offspring


class HasMutation(HasSelection1, Algorithm):
    """Extend class Algorithm with mutation properties and methods."""
    mutation: Mutation

    def mutate(self, phenotypes):
        """Extends algorithm call method with phenotypes mutation operation.
        :param phenotypes: List of evaluated phenotypes
        :returns: A list of varied phenotypes
        """
        self.logger.debug("mutation:\t%s", self.mutation)
        offspring = [self.mutation(phenotype) for phenotype in phenotypes]
        self.logger.debug("offspring=\t%s", offspring)
        return offspring


class HasSurvivalRate(HasSelection1, Algorithm):
    """Extend class Algorithm with survival properties and methods. When
    subclassing this methods, the algorithm protects the most performant
    phenotypes from the previous generation.
    """
    survival_rate: float = 0.4

    def skim(self, phenotypes):
        """Extends algorithm call method to protect a ratio of phenotypes.
        :param phenotypes: List of evaluated phenotypes
        :returns: A tuple with survivors and discarted phenotypes
        """
        self.logger.debug("survival_rate:\t%s", self.survival_rate)
        n_survivors = math.ceil(len(phenotypes) * self.survival_rate)
        survivors = phenotypes[:n_survivors]
        self.logger.debug("survivors=\t%s", survivors)
        return survivors, phenotypes[n_survivors:]


class Standard(HasSurvivalRate, HasCrossover, HasMutation, Algorithm):
    """This algorithm reproduce the standard evolutionary algorithm.

    First, a selection procedure is applied to replace a fraction of the
    population with deep copies of the parental population. Second, applies
    crossover between selected copies, generating new phenotypes. Third,
    applies mutation to crossover offspring, generating new phenotypes.

    Before the selection procedure, the percentage of phenotypes with lowest
    score defined by (1.0 - `survival_rate`) are removed. Phenotypes filtered
    by the survival process are replaced by a selection of survivors.
    """
    # pylint: disable=too-many-arguments

    def run_cycle(self, phenotypes):
        """Execution entry point for the algorithm.
        :param phenotypes: List of evaluated phenotypes
        :returns: A list of varied phenotypes
        """
        self.logger.debug("survival_phenotypes=\t%s", phenotypes)
        survivors, rest = self.skim(phenotypes)
        selected1, selected2 = self.select(phenotypes, len(rest))
        offspring = self.cross(selected1, selected2)
        offspring = self.mutate(offspring)
        self.logger.debug("simple_offspring=\t%s", offspring)
        return survivors + offspring
