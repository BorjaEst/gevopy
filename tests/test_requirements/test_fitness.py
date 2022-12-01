"""Module to test fitness requirements for evolution algorithms"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from inspect import ismethod, signature

from pytest import fixture, mark

from tests import fitnesses


# Module fixtures ---------------------------------------------------
@fixture(scope="class", params=[False, True])
def use_cache(request):
    """Fixture to enable or disable cache on fitness evaluation"""
    return request.param


@fixture(scope="class", params=['synchronous', 'threads', 'processes'])
def scheduler(request):
    """Fixture to select the scheduler to use on fitness evaluation"""
    return request.param


@fixture(scope="class")
def scores(population, use_fitness):
    """Fixture to return population scores"""
    return [ph.score for ph in population]


@fixture(scope="class", autouse=True)
def use_fitness(fitness, population):
    """Fixture to run fitness evaluation on the phenotypes population"""
    fitness(population)


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Fitness instances attributes"""

    def test_is_callable(self, fitness):
        """Test fitness is a callable with arity 1"""
        assert callable(fitness)
        assert len(signature(fitness).parameters) == 1

    def test_attr_score(self, fitness):
        """Test score is a fitness method"""
        assert hasattr(fitness, "score")
        assert ismethod(fitness.score)


class ExecutionRequirements:
    """Tests group for Fitness execution features"""

    def test_score_result(self, population):
        """Test all evaluated phenotypes have a float score attr"""
        assert all(hasattr(p, "score") for p in population)
        assert all(isinstance(p.score, float) for p in population)

    @mark.parametrize("use_cache", [False], indirect=True)
    def test_no_cache(self, fitness, population, scores):
        """Test when cache=False phenotypes are reevaluated"""
        fitness(population)  # Run fitness a second round
        assert scores != [ph.score for ph in population]

    @mark.parametrize("use_cache", [True], indirect=True)
    def test_run_cache(self, fitness, population, scores):
        """Test when cache=True phenotypes are not reevaluated"""
        fitness(population)  # Run fitness a second round
        assert scores == [ph.score for ph in population]

    def test_setup_executed(self, fitness):
        """Test set up function is executed before evaluation"""
        assert hasattr(fitness, "executed")


# Parametrization ---------------------------------------------------
class TestFitness(AttrRequirements, ExecutionRequirements):
    """Parametrization for testing using TimeFitness"""

    @fixture(scope="class", params=["TimeFitness"])
    def fitness(self, request, use_cache, scheduler):
        """Parametrization to define the fitness method to use"""
        fitness = fitnesses.__dict__[request.param]
        return fitness(cache=use_cache, scheduler=scheduler)
