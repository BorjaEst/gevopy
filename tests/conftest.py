"""Module for evolution requirements fixtures"""
# pylint: disable=redefined-outer-name

import random

from pytest import fixture

from gevopy.tools import crossover as crossover_tools
from gevopy.tools import mutation as mutation_tools
from gevopy.tools import selection as selection_tools
from tests import genotypes


@fixture(scope="function", autouse=True)
def set_random_seed():
    """Fix the random seed for repeatable testing"""
    random.seed(1)


@fixture(scope="package", params=["OneHaploid", "OneDiploid"])
def genotype(request):
    """Fixture to return the phenotype generator"""
    return genotypes.__dict__[request.param]


@fixture(scope="package")
def phenotype(genotype):
    """Fixture to return a phenotype instance"""
    return genotype()


@fixture(scope="package", params=[10, 20])
def population_size(request):
    """Parametrization for the number of phenotypes in the population"""
    return request.param


@fixture(scope="package")
def population_gen(genotype, population_size):
    """Fixture to return the population generator"""
    return lambda: [genotype() for _ in range(population_size)]


@fixture(scope="class")
def population(population_gen):
    """Fixture to return a population instance"""
    return population_gen()


@fixture(scope="class", params=[0, 1, 5, 20])
def selection_size(request):
    """Parametrization for the number of phenotypes to select"""
    return request.param
