"""Module to test evolution experiment sessions"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from copy import deepcopy
from inspect import ismethod

from pytest import fixture, mark, raises

import gevopy as ea
from gevopy.algorithms import Algorithm
from gevopy.fitness import FitnessModel


# Module fixtures ---------------------------------------------------
@fixture(scope="class", params=[5])
def max_generation(request):
    """Parametrization for the maximum generations to run on session"""
    return request.param


@fixture(scope="class", params=[0.8])
def max_score(request):
    """Parametrization for the maximum score to achieve on session"""
    return request.param


@fixture(scope="class")
def experiment(db_interface):
    """Fixture to generate an experiment for testing"""
    return ea.Experiment(database=db_interface)


@fixture(scope="class")
def execution(session, max_generation, max_score):
    """Fixture to run an experiment session and return execution"""
    return session.run(max_generation=max_generation, max_score=max_score)


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Session instances attributes"""

    def test_attr_fitness(self, session):
        """Test fitness is instance of FitnessModel"""
        assert hasattr(session, "fitness")
        assert isinstance(session.fitness, FitnessModel)

    def test_attr_algorithm(self, session):
        """Test algorithm is instance of Algorithm"""
        assert hasattr(session, "algorithm")
        assert isinstance(session.algorithm, Algorithm)


class ExecRequirements:
    """Tests group for session execution"""

    @mark.parametrize("max_score", [None], indirect=True)
    def test_generation_stop(self, execution, max_generation):
        """Test execution stops when maximum generation is reached"""
        assert execution.generation == max_generation
        assert execution.best_score > 0.0

    @mark.parametrize("max_generation", [None], indirect=True)
    def test_score_stop(self, execution, max_score):
        """Test execution stops when maximum score is reached"""
        assert execution.best_score >= max_score
        assert execution.generation >= 0

    def test_attr_generation(self, execution):
        """Test generation attr returns int after first execution"""
        assert hasattr(execution, "generation")
        assert isinstance(execution.generation, int)

    def test_attr_score(self, execution):
        """Test score attr returns float/int after first execution"""
        assert hasattr(execution, "best_score")
        assert isinstance(execution.best_score, (float, int))


class ErrRequirements:
    """Tests group for session exceptions requirements"""

    def test_unknown_args(self, session, max_score):
        """Test score attr returns float/int after first execution"""
        with raises(TypeError):
            session.run(unknown_kwarg="something", max_score=max_score)


# Parametrization ---------------------------------------------------
class TestSessions(AttrRequirements, ExecRequirements, ErrRequirements):
    """Parametrization for genetic evolution 'Session'"""

    @fixture(scope="class")
    def session(self, experiment, population, algorithm, fitness):
        """Fixture to open and return an experiment session for evolution"""
        with experiment.session() as session:
            session.add_phenotypes(population)
            session.algorithm = algorithm()
            session.fitness = fitness()
            yield session
            session.del_experiment()

    def test_reset_score(self, session):
        """Test reset_score resets phenotype scores"""
        session.run(max_generation=1)
        assert hasattr(session, "reset_score")
        assert ismethod(session.reset_score)
        session.reset_score()
        assert all(x.score == None for x in session._population)
