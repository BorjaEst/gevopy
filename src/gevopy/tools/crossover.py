"""The :mod:`crossover` module is intended to contain abstract and specific
classes to design your evolution algoritms.

Crossover is the stage of a genetic algorithm in which individual genomes
are crossed and combined in the population for breeding.

A rework form:
https://github.com/DEAP/deap/blob/master/deap/tools/crossover.py
"""
# pylint: disable=too-few-public-methods

import builtins
from abc import ABC, abstractmethod

import numpy as np

from gevopy import genetics, utils

methods = {"OnePoint", "TwoPoint", "MultiPoint", "Uniform"}
__all__ = methods.union({"Crossover"})


class Crossover(ABC):
    """Base class for crossover methods. In genetic algorithms and
    evolutionary computation, crossover, also called recombination, is
    a genetic operator used to combine the genetic information of two
    parents to generate new offspring. It is one way to stochastically
    generate new solutions from an existing population, and is analogous
    to the crossover that happens during sexual reproduction in biology.
    """

    def __call__(self, phenotype_1, phenotype_2):
        """Executes the crossover between phenotypes.
        :param phenotype_1: First phenotype to apply crossover
        :param phenotype_2: Second phenotype to apply crossover
        :return: Crossover phenotypes
        """
        match (phenotype_1, phenotype_2):
            case _ if not isinstance(phenotype_1, genetics.GenotypeModel):
                raise ValueError("Expected 'GenotypeModel' for 'phenotype_1'")
            case _ if not isinstance(phenotype_2, genetics.GenotypeModel):
                raise ValueError("Expected 'GenotypeModel' for 'phenotype_2'")

        parents = phenotype_1, phenotype_2  # Short code
        children = tuple(phenotype.clone() for phenotype in parents)
        parents_id = [ph.id for ph in parents]
        generation = max(0, *[x.generation for x in parents]) + 1

        for child in children:  # Assign generation and parents
            child.generation = generation
            child.parents = parents_id

        if phenotype_1 != phenotype_2:  # Cross only if different parents
            self.cross_features(*[x.__dict__.values() for x in children])
        return children

    def cross_features(self, features_1, features_2):
        """Recursively crosses phenotype features. For example a list of
        diploids in the case of Eucaryote genotype.
        :param features_1: Phenotype 1 list of feature values
        :param features_2: Phenotype 2 list of feature values
        """
        for values in zip(features_1, features_2):
            if all(isinstance(v, genetics.Chromosome) for v in values):
                self.cross_chromosomes(values[0], values[1])
            elif all(isinstance(v, list) for v in values):
                self.cross_features(values[0], values[1])

    @abstractmethod
    def cross_chromosomes(self, chromosome_1, chromosome_2):
        """Executes the crossover between chromosome. The two chromosomes
        are modified in place and both keep their original length.
        :param chromosome_1: The first chromosome participating in the crossover
        :param chromosome_2: The second chromosome participating in the crossover
        """
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.class_validator

    @classmethod
    def class_validator(cls, value):
        """Validates the value is a correct Mutation type."""
        if not isinstance(value, cls):
            raise TypeError("'Mutation' type required")
        return value


class Uniform(Crossover):
    """Executes uniform point crossover on the input phenotypes chromosomes.
    Phenotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self, indpb=0.1):
        """Constructor for uniform point crossover.
        :param indpb: Crossover probability on each index
        """
        match type(indpb):
            case builtins.float if not 0.0 <= indpb <= 1.0:
                raise ValueError("Value for 'indpb' must be beween 0 and 1")
            case builtins.float:
                self.index_probability = indpb
            case _wrong_type:
                raise ValueError("Type for 'indpb' must be 'float'")

    def cross_chromosomes(self, chromosome_1, chromosome_2):
        """Executes the crossover between chromosomes. The two chromosomes
        are modified in place and both keep their original length.
        :param chromosome_1: The first chromosome participating in the crossover
        :param chromosome_2: The second chromosome participating in the crossover
        """
        mask = np.random.random(len(chromosome_1)) <= self.index_probability
        ch1, ch2 = chromosome_1, chromosome_2  # Code len reduction
        ch1[mask], ch2[mask] = ch2[mask], ch1[mask]


class MultiPoint(Crossover):
    """Executes a multiple point crossover on the input phenotypes chromosomes.
    Phenotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self, n):
        """Constructor for multiple point crossover.
        :param n: Amount of random index points to cross
        """
        match type(n):
            case builtins.int if n < 1:
                raise ValueError("Value for 'n' cannot be lower than 1")
            case builtins.int:
                self.number_points = n
            case _wrong_type:
                raise ValueError("Type for 'n' must be a positive 'int'")

    def cross_chromosomes(self, chromosome_1, chromosome_2):
        """Executes the crossover between chromosomes. The two chromosomes
        are modified in place and both keep their original length.
        :param chromosome_1: The first chromosome participating in the crossover
        :param chromosome_2: The second chromosome participating in the crossover
        """
        lengths = len(chromosome_1), len(chromosome_2)
        points = np.random.randint(min(*lengths), size=self.number_points)
        points.sort()
        utils.cross_chromosomes(chromosome_1, chromosome_2, points)


class OnePoint(MultiPoint):
    """Executes a one point crossover on the input phenotypes chromosomes.
    Phenotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self):
        """Constructor for one point crossover."""
        super().__init__(n=1)


class TwoPoint(MultiPoint):
    """Executes a two point crossover on the input phenotypes chromosomes.
    Phenotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self):
        """Constructor for two point crossover."""
        super().__init__(n=2)
