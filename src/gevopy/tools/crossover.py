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

    def __call__(self, genotype_1, genotype_2):
        """Executes the crossover between genotypes.
        :param genotype_1: First genotype to apply crossover
        :param genotype_2: Second genotype to apply crossover
        :return: Crossover genotypes
        """
        match (genotype_1, genotype_2):
            case _ if not isinstance(genotype_1, genetics.GenotypeModel):
                raise ValueError("Expected 'GenotypeModel' for 'genotype_1'")
            case _ if not isinstance(genotype_2, genetics.GenotypeModel):
                raise ValueError("Expected 'GenotypeModel' for 'genotype_2'")

        parents = genotype_1, genotype_2  # Short code
        children = tuple(genotype.clone() for genotype in parents)
        parents_id = [ph.id for ph in parents]
        generation = max(0, *[x.generation for x in parents]) + 1

        for child in children:  # Assign generation and parents
            child.generation = generation
            child.parents = parents_id

        if genotype_1 != genotype_2:  # Cross only if different parents
            self.cross_features(*[x.__dict__.values() for x in children])
        return children

    def cross_features(self, features_1, features_2):
        """Recursively crosses genotype features. For example a list of
        diploids in the case of Eucaryote genotype.
        :param features_1: genotype 1 list of feature values
        :param features_2: genotype 2 list of feature values
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
        :param chromosome_1: First chromosome participating in the crossover
        :param chromosome_2: Second chromosome participating in the crossover
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
    """Executes uniform point crossover on the input genotypes chromosomes.
    genotype chromosomes are crossed on equal indexes. The resulting
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
            case _:
                raise ValueError("Type for 'indpb' must be 'float'")

    def cross_chromosomes(self, chromosome_1, chromosome_2):
        """Executes the crossover between chromosomes. The two chromosomes
        are modified in place and both keep their original length.
        :param chromosome_1: First chromosome participating in the crossover
        :param chromosome_2: Second chromosome participating in the crossover
        """
        mask = np.random.random(len(chromosome_1)) <= self.index_probability
        ch1, ch2 = chromosome_1, chromosome_2  # Code len reduction
        ch1[mask], ch2[mask] = ch2[mask], ch1[mask]


class MultiPoint(Crossover):
    """Executes a multiple point crossover on the input genotypes chromosomes.
    genotype chromosomes are crossed on equal indexes. The resulting
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
            case _:
                raise ValueError("Type for 'n' must be a positive 'int'")

    def cross_chromosomes(self, chromosome_1, chromosome_2):
        """Executes the crossover between chromosomes. The two chromosomes
        are modified in place and both keep their original length.
        :param chromosome_1: First chromosome participating in the crossover
        :param chromosome_2: Second chromosome participating in the crossover
        """
        lengths = len(chromosome_1), len(chromosome_2)
        points = np.random.randint(min(*lengths), size=self.number_points)
        points.sort()
        utils.cross_chromosomes(chromosome_1, chromosome_2, points)


class OnePoint(MultiPoint):
    """Executes a one point crossover on the input genotypes chromosomes.
    genotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self):
        """Constructor for one point crossover."""
        super().__init__(n=1)


class TwoPoint(MultiPoint):
    """Executes a two point crossover on the input genotypes chromosomes.
    genotype chromosomes are crossed on equal indexes. The resulting
    chromosomes will respectively have the length of the other.
    """

    def __init__(self):
        """Constructor for two point crossover."""
        super().__init__(n=2)
