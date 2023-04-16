"""Module to test database operations for evolution algorithms."""
# pylint: disable=redefined-outer-name

import uuid

from pytest import fixture, mark


@fixture(scope="module", autouse=True)
def session(db_interface):
    """Fixture to start a graph database session for testing"""
    with db_interface.session() as session:
        yield session


@fixture(scope="function")
def experiment_name():
    """Fixture to generate an experiment name for testing"""
    return f"Experiment_{uuid.uuid4()}"


@fixture(scope="function", autouse=True)
def clean_experiment(session, experiment_name):
    """Fixture to start a graph database session for testing"""
    yield None
    session.del_experiment(experiment_name)


@fixture(scope="function", autouse=True)
def add_experiment(population, experiment_name):
    """Fixture to add experiment to some genotypes"""
    for genotype in population[::2]:
        genotype.experiment = experiment_name


@fixture(scope="function", autouse=True)
def add_parents(population):
    """Fixture to create parent relatioships between genotypes"""
    for child, parent in zip(population, population[1:]):
        child.parents = [parent.id]


@fixture(scope="function")
def genotypes(population):
    """Fixture to return genotypes ids from population"""
    return [p.dict(serialize=True) for p in population]


@fixture(scope="function")
def ids(population):
    """Fixture to return genotypes ids from population"""
    return [str(ph.id) for ph in population]


@mark.parametrize("db_interface", ["Neo4jInterface"], indirect=True)
def test_rwd_genotypes(session, genotypes, ids):
    """Test write, read and delete of genotypes in db"""
    assert ids == session.add_genotypes(genotypes)
    assert genotypes == session.get_genotypes(ids)
    assert all([id in ids for id in session.del_genotypes(ids)])
