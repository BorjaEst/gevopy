"""Module for evolution requirements fixtures"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import pytest
import itertools
import copy


@pytest.fixture(scope="module")
def crossovers(app):
    return app.crossovers


@pytest.fixture(scope="module")
def children(genotypes, app):
    genotypes = copy.deepcopy(genotypes)
    product = itertools.product(genotypes, repeat=2)
    [app.cross(*selected) for selected in product]
    return genotypes


@pytest.fixture(scope="module")
def evaluators(app):
    return app.evaluators


@pytest.fixture(scope="module")
def mutations(app):
    return app.mutations


@pytest.fixture(scope="module")
def mutated(genotypes, app):
    genotypes = copy.deepcopy(genotypes)
    [app.mutate(genotype) for genotype in genotypes]
    return genotypes


@pytest.fixture(scope="module")
def populations(app):
    populations = [app.spawn_population(g, 10) for g in app.genotypes]
    yield populations
    [app.kill_population(name) for name in populations]
