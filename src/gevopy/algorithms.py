"""The :mod:`algorithms` module is intended to contain some specific
algorithms in order to execute the most common evolutionary algorithms.

The methods used here are more for convenience than reference as the
implementation of every evolutionary algorithm may vary infinitely. Most
of the algorithms in this module use operators registered in the tools
package.

A rework form:
https://github.com/DEAP/deap/blob/master/deap/algorithms.py
"""

import logging
import math
from abc import ABC, abstractmethod

from gevopy import tools
from gevopy.tools.crossover import Crossover, OnePoint
from gevopy.tools.mutation import Mutation, SinglePoint
from gevopy.tools.selection import Selection, Uniform, Ponderated

# https://docs.python.org/3/howto/logging-cookbook.html
module_logger = logging.getLogger(__name__)


class Algorithm(ABC):
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

    def __init__(self) -> None:
        """Generic constructor for genetic algorithms."""
        self._name = self.__class__.__name__
        self._logger = logging.getLogger(f"{__name__}.{self._name}")

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

    def __init__(self, *args, selection1: Selection, **kwargs) -> None:
        """Generic constructor for genetic algorithms.
        :param selection1: Selection instance to apply on phenotypes
        """
        super().__init__(*args, **kwargs)
        self.selection1 = selection1

    @property
    def selection1(self):
        """Selection function to choose first phenotypes from population.
        :return: Evolution algorithm `Selection` instance
        """
        return self.__selection1

    @selection1.setter
    def selection1(self, selection):
        """Sets the selection1 function to use in the algorithm.
        :param selection: Evolution algorithm `Selection` instance
        """
        if not isinstance(selection, Selection):
            raise ValueError("Expected 'Selection' type")
        self.__selection1 = selection

    def select(self, phenotypes, n):
        """Extends algorithm call method with phenotypes selection operation.
        :param phenotypes: Pool of evaluated phenotypes
        :param n: Number of phenotype to select from pool
        :returns: A list of varied phenotypes
        """
        self._logger.debug("selection1:\t%s", self.selection1)
        selected1 = self.selection1(phenotypes, n)
        self._logger.debug("selection1=\t%s", selected1)
        return selected1


class HasSelection2(HasSelection1, Algorithm):
    """Extend class Algorithm with a second selection round of phenotypes."""

    def __init__(self, *args, selection2: Selection, **kwargs) -> None:
        """Generic constructor for genetic algorithms.
        :param selection2: Selection instance to apply on phenotypes
        """
        super().__init__(*args, **kwargs)
        self.selection2 = selection2

    @property
    def selection2(self):
        """Selection function to choose second phenotypes from population.
        :return: Evolution algorithm `Selection` instance
        """
        return self.__selection2

    @selection2.setter
    def selection2(self, selection):
        """Sets the selection2 function to use in the algorithm.
        :param selection: Evolution algorithm `Selection` instance
        """
        assert isinstance(selection, Selection)
        self.__selection2 = selection

    def select(self, phenotypes, n):
        """Extends algorithm call method with phenotypes selection operation.
        :param phenotypes: Pool of evaluated phenotypes
        :param n: Number of phenotype to select from pool 
        :returns: A list of varied phenotypes
        """
        selected1 = super().select(phenotypes, n)
        self._logger.debug("selection2:\t%s", self.selection2)
        selected2 = self.selection2(phenotypes, n)
        self._logger.debug("selection2=\t%s", selected2)
        return selected1, selected2


class HasCrossover(HasSelection2, Algorithm):
    """Extend class Algorithm with crossover properties and methods."""

    def __init__(self, *args, crossover: Crossover, **kwargs) -> None:
        """Generic constructor for genetic algorithms.
        :param crossover: Crossover instance to apply on selected phenotypes
        """
        super().__init__(*args, **kwargs)
        self.crossover = crossover

    @property
    def crossover(self):
        """Crossover function to cross two phenotypes for outspring.
        :return: Evolution algorithm `Crossover` instance
        """
        return self.__crossover

    @crossover.setter
    def crossover(self, crossover):
        """Sets the crossover function to use in the algorithm.
        :param crossover: Evolution algorithm `Crossover` instance
        """
        if not isinstance(crossover, Crossover):
            raise ValueError("Expected 'Crossover' type or 'None'")
        self.__crossover = crossover

    def cross(self, selected1, selected2):
        """Extends algorithm call method with phenotypes crossover operation.
        :param selected1: List 1 of phenotypes to cross
        :param selected2: List 2 of phenotypes to cross
        :returns: A list of varied phenotypes
        """
        self._logger.debug("crossover:\t%s", self.crossover)
        selections = zip(selected1, selected2)
        offspring = [self.crossover(x, y)[0] for x, y in selections]
        self._logger.debug("offspring=\t%s", offspring)
        return offspring


class HasMutation(HasSelection1, Algorithm):
    """Extend class Algorithm with mutation properties and methods."""

    def __init__(self, *args, mutation: Mutation, **kwargs) -> None:
        """Generic constructor for genetic algorithms.
        :param mutation: Mutation instance to apply on selected/offspring
        """
        super().__init__(*args, **kwargs)
        self.mutation = mutation

    @property
    def mutation(self):
        """Mutation function to mutate offspring phenotypes.
        :return: Evolution algorithm `Mutation` instance
        """
        return self.__mutation

    @mutation.setter
    def mutation(self, mutation):
        """Sets the mutation function to use in the algorithm.
        :param mutation: Evolution algorithm `Mutation` instance
        """
        if not isinstance(mutation, Mutation):
            raise ValueError("Expected 'Mutation' type or 'None'")
        self.__mutation = mutation

    def mutate(self, phenotypes):
        """Extends algorithm call method with phenotypes mutation operation.
        :param phenotypes: List of evaluated phenotypes
        :returns: A list of varied phenotypes
        """
        self._logger.debug("mutation:\t%s", self.mutation)
        offspring = [self.mutation(phenotype) for phenotype in phenotypes]
        self._logger.debug("offspring=\t%s", offspring)
        return offspring


class HasSurvivalRate(HasSelection1, Algorithm):
    """Extend class Algorithm with survival properties and methods. When
    subclassing this methods, the algorithm protects the most performant
    phenotypes from the previous generation.
    """

    def __init__(self, *args, survival_rate: float = 0.4, **kwargs) -> None:
        """Generic constructor for survival algorithms.
        :param survival_rate: Percentage of survival, default is 0.4
        """
        super().__init__(*args, **kwargs)
        self.survival_rate = survival_rate

    @property
    def survival_rate(self):
        """Survival rate to filter reproduction phenotypes.
        :return: Float between 0.0 and 1.0
        """
        return self.__survival_rate

    @survival_rate.setter
    def survival_rate(self, survival_rate):
        """Sets the survival rate value to use in the algorithm.
        :param survival_rate: Evolution algorithm `Survival_rate` instance
        """
        if not isinstance(survival_rate, float):
            raise ValueError("Expected 'float' type value for survival rate")
        if not 0.0 <= survival_rate <= 1.0:
            raise ValueError("Expected 'survival_rate' value between 0 and 1")
        self.__survival_rate = survival_rate

    def skim(self, phenotypes):
        """Extends algorithm call method to protect a ratio of phenotypes.
        :param phenotypes: List of evaluated phenotypes
        :returns: A tuple with survivors and discarted phenotypes
        """
        self._logger.debug("survival_rate:\t%s", self.survival_rate)
        n_survivors = math.ceil(len(phenotypes) * self.survival_rate)
        survivors = phenotypes[:n_survivors]
        self._logger.debug("survivors=\t%s", survivors)
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

    def __init__(
        self,
        selection1: Selection = Ponderated(),  # Main selection operator
        selection2: Selection = Uniform(),  # Crossover selection operator
        crossover: Crossover = OnePoint(),  # Crossover operator
        mutation: Mutation = SinglePoint(),  # Mutation operator
        survival_rate: float = 0.0,  # Survival rate value
    ) -> None:
        """Generic constructor for a survival genetic algorithms.
        :param selection1: Selection instance for first partner selection
        :param crossover: Crossover instance to apply on selected phenotypes
        :param mutation: Mutation instance to apply on selected/offspring
        :param selection2: Selection instance to apply on phenotypes
        :param survival_rate: Percentage of survival, default is 0.0
        """
        super().__init__(
            selection1=selection1,
            selection2=selection2,
            crossover=crossover,
            mutation=mutation,
            survival_rate=survival_rate,
        )

    def run_cycle(self, phenotypes):
        """Execution entry point for the algorithm.
        :param phenotypes: List of evaluated phenotypes
        :returns: A list of varied phenotypes
        """
        self._logger.debug("survival_phenotypes=\t%s", phenotypes)
        survivors, rest = self.skim(phenotypes)
        selected1, selected2 = self.select(phenotypes, len(rest))
        offspring = self.cross(selected1, selected2)
        offspring = self.mutate(offspring)
        self._logger.debug("simple_offspring=\t%s", offspring)
        return survivors + offspring
