"""Module for evolution requirements fixtures"""
# pylint: disable=redefined-outer-name

import os

from neo4j import GraphDatabase
from pytest import fixture
from gevopy.database import Neo4jInterface, EmptyInterface

import examples.algorimths
import examples.evaluation
import examples.genotypes

NEO4J_DRIVER = dict(
    uri=os.getenv('TESTING_NEO4J_URI'),
    auth=os.getenv('TESTING_NEO4J_AUTH'),
)


@fixture(scope="session", params=[NEO4J_DRIVER])
def driver_kwds(request):
    """Fixture to generate a neo4j database driver"""
    # pylint: disable=not-context-manager
    with GraphDatabase.driver(**request.param) as driver:
        driver.verify_connectivity()
    return request.param


@fixture(scope="session", params=["Neo4jInterface", "EmptyInterface"])
def db_interface(request, driver_kwds):
    """Fixture to return the experiment interface for the database"""
    match request.param:
        case "Neo4jInterface":
            interface = Neo4jInterface(**driver_kwds)
        case _:
            interface = EmptyInterface()
    yield interface
    interface.close()


@fixture(scope="session", params=["Bacteria", "JackJumper"])
def genotype(request):
    """Fixture to return the phenotype generator from example"""
    return examples.genotypes.__dict__[request.param]


@fixture(scope="session", params=["Random"])
def fitness(request):
    """Fixture to return fitness class from example"""
    return examples.evaluation.__dict__[request.param]


@fixture(scope="session", params=["BasicUniform", "BasicPonderated"])
def algorithm(request):
    """Fixture to return the algorithm definition from example"""
    return examples.algorimths.__dict__[request.param]


@fixture(scope="session", params=[10, 20])
def population_size(request):
    """Parametrization for the number of phenotypes in the population"""
    return request.param


@fixture(scope="session")
def population_gen(genotype, population_size):
    """Fixture to return the population generator"""
    return lambda: [genotype() for _ in range(population_size)]


@fixture(scope="module")
def population(population_gen):
    """Fixture to return a population instance"""
    return population_gen()
