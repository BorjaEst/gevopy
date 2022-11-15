"""Module for evolution requirements fixtures"""
# pylint: disable=redefined-outer-name

import random

from pytest import fixture

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
def phenotype(phenotype_gen):
    """Fixture to return a phenotype instance"""
    return phenotype_gen()
