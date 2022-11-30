"""Module to test database operations for evolution algorithms."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# TODO: Load database configuration from configuration file or .env

from pytest import fixture

from gevopy import database


@fixture(scope="module", autouse=True)
def session(driver):
    """Fixture to start a graph database session for testing"""
    with database.GraphSession(driver) as session:
        yield session


@fixture(scope="class", autouse=True)
def add_experiment(population, experiment):
    """Fixture to add experiment to some phenotypes"""
    for phenotype in population[::2]:
        phenotype.experiment = experiment


@fixture(scope="class", autouse=True)
def add_parents(population):
    """Fixture to create parent relatioships between phenotypes"""
    for child, parent in zip(population, population[1:]):
        child.parents = [parent.id]


@fixture(scope="class")
def phenotypes(population):
    """Fixture to return phenotypes ids from population"""
    return [p.dict(serialize=True) for p in population]


@fixture(scope="class")
def ids(population):
    """Fixture to return phenotypes ids from population"""
    return [str(ph.id) for ph in population]


def test_rw_phenotypes(session, phenotypes, ids):
    """Test write and read of phenotypes in db"""
    assert ids == session.add_phenotypes(phenotypes)
    assert phenotypes == session.get_phenotypes(ids)
