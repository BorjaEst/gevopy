"""Module to test fitness requirements for evolution algorithms"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from inspect import ismethod, signature

from pytest import fixture, mark


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
def pool(evaluator, population):
    """Fixture to run fitness evaluation on the genotypes population"""
    return evaluator(population)


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Fitness instances attributes"""

    def test_is_callable(self, evaluator):
        """Test fitness is a callable with arity 1"""
        assert callable(evaluator)
        assert len(signature(evaluator).parameters) == 1

    def test_attr_score(self, evaluator):
        """Test score is a fitness method"""
        assert hasattr(evaluator, "score")
        assert ismethod(evaluator.score)


class ExecutionRequirements:
    """Tests group for Fitness execution features"""

    @mark.parametrize("use_cache", [False], indirect=True)
    def test_no_cache(self, evaluator, population, pool):
        """Test when cache=False genotypes are reevaluated"""
        assert pool.scores != evaluator(population).scores

    @mark.parametrize("use_cache", [True], indirect=True)
    def test_run_cache(self, evaluator, population, pool):
        """Test when cache=True genotypes are not reevaluated"""
        assert pool.scores == evaluator(population).scores

    def test_setup_executed(self, evaluator, pool):
        """Test set up function is executed before evaluation"""
        assert hasattr(evaluator, "executed")


# Parametrization ---------------------------------------------------
class TestFitness(AttrRequirements, ExecutionRequirements):
    """Parametrization for testing using TimeFitness"""

    @fixture(scope="class")
    def evaluator(self, fitness, use_cache, scheduler):
        """Parametrization to define the fitness method to use"""
        return fitness(cache=use_cache, scheduler=scheduler)
