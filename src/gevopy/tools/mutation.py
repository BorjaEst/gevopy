"""The :mod:`mutation` module is intended to contain abstract and specific
classes to design your evolution algoritms.

Mutation is the stage of a genetic algorithm in which individual genomes
from an outspring are changed in order to generate new features.

https://github.com/DEAP/deap/blob/master/deap/tools/mutation.py
"""
# pylint: disable=too-few-public-methods

from abc import ABC, abstractmethod
from copy import deepcopy

import numpy as np

from gevopy import genetics

methods = {"SinglePoint"}
__all__ = methods.union({"Mutation"})


class Mutation(ABC):
    """Mutation is a genetic operator used to maintain genetic diversity
    from one generation of a population of genetic algorithm chromosomes
    to the next. It is analogous to biological mutation.

    A mutation operator involves a probability that an arbitrary bit in
    a genetic chain will be flipped from its original state.

    Mutation operators are used in an attempt to avoid local minima by
    preventing the population of chromosomes from becoming too similar
    to each other, thus slowing or even stopping convergence to the global
    optimum. This reasoning also leads most GA systems to avoid only taking
    the fittest of the population in generating the next generation, but
    rather selecting a random (or semi-random) set with a weighting toward
    those that are fitter.

    For different genome types, different mutation types are suitable.
    """

    def __call__(self, genotype):
        """Executes the mutation on a genotype. If the genotype was never
        evaluated, then clone is an exact copy maintaining id and parents.
        :param genotype: The genotype to mutate
        :return: Mutated genotype
        """
        match genotype:
            case _ if not isinstance(genotype, genetics.GenotypeModel):
                raise ValueError("Expected 'GenotypeModel' for 'genotype'")

        genotype_copy = deepcopy(genotype)
        self.mutate_features(genotype_copy.__dict__.values())
        return genotype_copy

    def mutate_features(self, features):
        """Recursively mutates genotype features. For example a list of
        diploids in the case of Eucaryote genotype.
        :param features: genotype list of feature values
        """
        for value in features:
            if isinstance(value, genetics.Chromosome):
                self.mutate_chromosome(chromosome=value)
            elif isinstance(value, list):
                self.mutate_features(features=value)

    @abstractmethod
    def mutate_chromosome(self, chromosome):
        """Executes mutation on a specific object using a probability mask.
        :param chromosome: The value chain where to apply mutation
        :param mask: Boolean array indicating where to apply mutation
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


class SinglePoint(Mutation):
    """Executes single point mutation over a property array. This mutation
    method generates a random variable for each bit in a chain sequence to
    evaluate whether or not a particular bit will be flipped.
    For Example:
    - chromosome.chain => [0110101011101011000101010010]
                            ↓    ↓↓↓ ↓    ↓ ↓    ↓ ↓↓↓
    - chromosome.chain => [0010100101001010010101111100]

    The chromosome chain is modified in place and keep hist original length.
    This mutation procedure is based on the biological point mutation.
    """

    def __init__(self, mutpb=0.05):
        """Mutation generic constructor.
        :param mutpb: Probability of each slot mutation, defaults to 0.05
        """
        self.mutation_probability = mutpb

    def mutate_chromosome(self, chromosome):
        """Executes the mutation. The chromosome chain is modified in place.
        :param chromosome: Chromosome to be mutated
        """
        mask = np.random.random(chromosome.size) <= self.mutation_probability
        chromosome[mask] = chromosome[mask].__mutate__()
