"""Module to test evolution algorithm requirements"""
# pylint: disable=redefined-outer-name

from pytest import fixture, mark

from gevopy import algorithms, genetics
from gevopy.tools import crossover, mutation, selection


# Module fixtures ---------------------------------------------------
@fixture(scope="class", autouse=True)
def score_phenotypes(population):
    """Fixture to add a score to a population of phenotypes"""
    for index, phenotype in enumerate(population):
        phenotype.score = index


# Requirements ------------------------------------------------------
class AttrRequirements:
    """Tests group for Algorithm instances attributes"""

    def test_attr_selection1(self, algorithm):
        """Test selection1 is instance of tools Selection"""
        assert hasattr(algorithm, "selection1")
        assert isinstance(algorithm.selection1, selection.Selection)

    def test_attr_selection2(self, algorithm):
        """Test selection2 is instance of tools Selection"""
        assert hasattr(algorithm, "selection2")
        assert isinstance(algorithm.selection2, selection.Selection)

    def test_attr_crossover(self, algorithm):
        """Test crossover is instance of tools Crossover"""
        assert hasattr(algorithm, "crossover")
        assert isinstance(algorithm.crossover, crossover.Crossover)

    def test_attr_mutation(self, algorithm):
        """Test mutation is instance of tools Mutation"""
        assert hasattr(algorithm, "mutation")
        assert isinstance(algorithm.mutation, mutation.Mutation)


class ExecutionRequirements:
    """Tests group for Algorithm execution features"""

    def test_return_run(self, result):
        """Test algorithm returns a list of genotype models"""
        assert all(isinstance(x, genetics.GenotypeModel) for x in result)

    @mark.parametrize("survival_rate", [0.0], indirect=True)
    def test_no_ids_keep(self, result, population):
        """Test algorithm return phenotypes are completelly new"""
        assert not any(x in population for x in result)

    @mark.parametrize("survival_rate", [0.5], indirect=True)
    def test_some_ids_change(self, result, population):
        """Test algorithm return phenotypes has new members"""
        assert not all(x in population for x in result)

    @mark.parametrize("survival_rate", [0.5], indirect=True)
    def test_some_ids_keep(self, result, population):
        """Test algorithm return phenotypes are completelly new"""
        assert any(x in population for x in result)

    @mark.parametrize("survival_rate", [1.0], indirect=True)
    def test_all_ids_keep(self, result, population):
        """Test algorithm returns no new phenotypes"""
        assert all(x in population for x in result)


# Parametrization ---------------------------------------------------
class TestStandard(AttrRequirements, ExecutionRequirements):
    """Parametrization for 'Standard' algorithm"""

    @fixture(scope="class")
    def selections(self, selection1, selection2):
        """Parametrization to define the algorithm configuration to use"""
        return dict(selection1=selection1, selection2=selection2)

    @fixture(scope="class")
    def evolution(self, crossover, mutation):
        """Parametrization to define the algorithm configuration to use"""
        return dict(crossover=crossover, mutation=mutation)

    @fixture(scope="class")
    def config(self, survival_rate):
        """Parametrization to define the algorithm configuration to use"""
        return dict(survival_rate=survival_rate)

    @fixture(scope="class")
    def algorithm(self, selections, evolution, config):
        """Parametrization to define the algorithm configuration to use"""
        return algorithms.Standard(**selections, **evolution, **config)

    @fixture(scope="class")
    def result(self, algorithm, population):
        """Fixture to run an algorithm cycle"""
        return algorithm(population)
