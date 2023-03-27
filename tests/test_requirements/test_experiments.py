"""Module to test evolution experiments"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import uuid
from inspect import ismethod


from pytest import fixture, mark

import gevopy as ea
from gevopy.database import Interface


# Module fixtures ---------------------------------------------------
@fixture(scope="class")
def experiment_name():
    """Fixture to generate an experiment name for testing"""
    return f"Experiment_{uuid.uuid4()}"


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Experiment instances attributes"""

    def test_attr_name(self, experiment):
        """Test experiment has a correct 'name' attribute"""
        assert hasattr(experiment, "name")
        assert isinstance(experiment.name, str)

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

    def test_context_session(self, experiment):
        """Test experiment has a session context manager"""
        assert hasattr(experiment, "session")
        assert ismethod(experiment.session)  # TODO: Test context manager

    def test_method_close(self, experiment):
        """Test experiment can be closed when experiment ends"""
        assert hasattr(experiment, "close")
        assert ismethod(experiment.close)  # TODO: Test correct closing


# Parametrization ---------------------------------------------------
class TestExperiments(AttrRequirements, ExecRequirements):
    """Parametrization for genetic evolution 'Experiment'"""

    @fixture(scope="class")
    def experiment(self, experiment_name, db_interface):
        """Parametrization to define the algorithm configuration to use"""
        return ea.Experiment(name=experiment_name, database=db_interface)
