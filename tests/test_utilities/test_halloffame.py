"""Module to test HallOfFamme utility for evolution algorithms."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from pytest import fixture, mark

from examples.genotypes import Bacteria as Genotype
from gevopy import tools


@fixture(scope="function")
def halloffame(maxsize):
    """Instantiates and returns a HallOfFame"""
    return tools.HallOfFame(maxsize)


@fixture(scope="function", autouse=True)
def update(halloffame, population1, population2):
    """Updates Hall Of Fame with pools of phenotypes"""
    halloffame.update(tools.Pool(population1))
    halloffame.update(tools.Pool(population2))


@fixture(scope="function")
def newsize(request, halloffame, update):
    """Updates Hall Of Fame with pool of phenotypes"""
    halloffame.maxsize = request.param
    return request.param


@mark.parametrize("maxsize", [1, 3, 5, 9])
@mark.parametrize("population1", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
@mark.parametrize("population2", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
def test_maxsize(halloffame, maxsize):
    """Test the length of the Hall Of Fame never passes maxsize"""
    assert len(halloffame) <= maxsize


@mark.parametrize("maxsize", [1, 3, 5, 9])
@mark.parametrize("population1", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
@mark.parametrize("population2", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
def test_order(halloffame):
    """Test the elements in the Hall Of Fame are ordered by score"""
    sorted_scores = sorted([x.score for x in halloffame], reverse=True)
    assert [x.score for x in halloffame] == sorted_scores


@mark.parametrize("newsize", [1, 9], indirect=True)
@mark.parametrize("maxsize", [1, 5, 9])
@mark.parametrize("population1", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
@mark.parametrize("population2", [[Genotype(score=x) for x in [0, 1, 5, 7]]])
def test_newsize(halloffame, newsize):
    """Test the length of the Hall Of Fame never passes newsize"""
    assert len(halloffame) <= newsize
