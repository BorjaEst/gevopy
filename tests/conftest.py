"""Module for evolution requirements fixtures"""
# pylint: disable=redefined-outer-name

import random
import uuid
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


@fixture(scope="session", params=["Neo4jInterface"])
def db_interface(request, driver_kwds):
    """Fixture to return the experiment interface for the database"""
    match request.param:
        case "Neo4jInterface":
            interface = Neo4jInterface(**driver_kwds)
        case _default:
            interface = EmptyInterface()
    yield interface
    interface.close()


@fixture(scope="class", params=["Bacteria", "JackJumper"])
def genotype(request):
    """Fixture to return the phenotype generator from example"""
    return examples.genotypes.__dict__[request.param]


@fixture(scope="class", params=["Random"])
def fitness(request):
    """Fixture to return fitness class from example"""
    return examples.evaluation.__dict__[request.param]


@fixture(scope="class", params=["BasicUniform", "BasicPonderated"])
def algorithm(request):
    """Fixture to return the algorithm definition from example"""
    return examples.algorimths.__dict__[request.param]


@fixture(scope="class")
def experiment_name():
    """Fixture to generate an experiment name for testing"""
    return f"Experiment_{uuid.uuid4()}"


@fixture(scope="class", params=[10, 20])
def population_size(request):
    """Parametrization for the number of phenotypes in the population"""
    return request.param


@fixture(scope="class")
def population_gen(genotype, population_size):
    """Fixture to return the population generator"""
    return lambda: [genotype() for _ in range(population_size)]


@fixture(scope="class")
def population(population_gen):
    """Fixture to return a population instance"""
    return population_gen()


@fixture(scope="function", autouse=True)
def set_random_seed():
    """Fix the random seed for repeatable testing"""
    random.seed(1)
