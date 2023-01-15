"""Module to test evolution experiments"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import uuid

from pytest import fixture, mark, raises

import gevopy as ea
from gevopy.algorithms import Algorithm
from gevopy.database import Interface
from gevopy.fitness import FitnessModel


# Module fixtures ---------------------------------------------------
@fixture(scope="class", params=[5])
def max_generation(request):
    """Parametrization for the maximum generations to run on experiment"""
    return request.param


@fixture(scope="class", params=[0.8])
def max_score(request):
    """Parametrization for the maximum score to achieve on experiment"""
    return request.param


@fixture(scope="class")
def experiment_name():
    """Fixture to generate an experiment name for testing"""
    return f"Experiment_{uuid.uuid4()}"


@fixture(scope="class")
def session(experiment, population):
    """Fixture to open and return an experiment session for evolution"""
    with experiment.session() as session:
        session.add_phenotypes(population)
        yield session
        session.del_experiment()


@fixture(scope="class")
def execution(session, max_generation, max_score):
    """Fixture to run an experiment and return execution"""
    return session.run(max_generation=max_generation, max_score=max_score)


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Experiment instances attributes"""

    def test_attr_name(self, experiment):
        """Test experiment has a correct 'name' attribute"""
        assert hasattr(experiment, "name")
        assert isinstance(experiment.name, str)

    def test_attr_fitness(self, experiment):
        """Test fitness is instance of FitnessModel"""
        assert hasattr(experiment, "fitness")
        assert isinstance(experiment.fitness, FitnessModel)

    def test_attr_algorithm(self, experiment):
        """Test algorithm is instance of Algorithm"""
        assert hasattr(experiment, "algorithm")
        assert isinstance(experiment.algorithm, Algorithm)

    @mark.parametrize("db_interface", ["Neo4jInterface"], indirect=True)
    def test_neo4j_database(self, experiment):
        """Test experiment has a correct 'database' attribute"""
        assert hasattr(experiment, "database")
        assert isinstance(experiment.database, Interface)

    @mark.parametrize("db_interface", ["EmptyInterface"], indirect=True)
    def test_none_database(self, experiment):
        """Test experiment has a correct 'database' attribute"""
        assert hasattr(experiment, "database")
        assert isinstance(experiment.database, Interface)


class ExecRequirements:
    """Tests group for experiment execution"""

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
    """Tests group for experiment exceptions requirements"""

    def test_unknown_args(self, session, max_score):
        """Test score attr returns float/int after first execution"""
        with raises(TypeError):
            session.run(unknown_kwarg="something", max_score=max_score)


# Parametrization ---------------------------------------------------
class TestExperiments(AttrRequirements, ExecRequirements, ErrRequirements):
    """Parametrization for genetic evolution 'Experiment'"""

    @fixture(scope="class")
    def experiment(self, experiment_name, db_interface, fitness, algorithm):
        """Parametrization to define the algorithm configuration to use"""
        return ea.Experiment(
            name=experiment_name,
            database=db_interface,
            fitness=fitness(),
            algorithm=algorithm(),
        )
